import random
import string
import authorization
from oauth2client.client import Credentials

from flask import Flask
from flask import render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

app = Flask(__name__)

# start database engine
db_name = 'sqlite:///itemcatalog.db'
engine = create_engine(db_name)
Base.metadata.bind = engine

###############################################################
#
# API endpoint functions
#
################################################################


@app.route("/get_categories/", methods=['GET'])
def getCategoryAndItems():
    """
    create json object from the item catalog
    :return:
    """
    categories_json = []
    session = create_session()
    categories = [x.serialize for x in session.query(Category).all()]
    for cat in categories:
        items = [x.serialize for x in session.query(Item)
                  .filter(Item.category_id == cat['id']).all()]
        cat['items'] = items
        categories_json.append(cat)
    close_session(session)
    json = {'category': categories_json}
    return str(json)


@app.route("/get_iteminfo/<string:item>", methods=['GET'])
def getItemInfo(item):
    """
    create json object from the item catalog item
    :return:
    """
    categories_json = []
    session = create_session()
    categories = [x.serialize for x in session
                   .query(Category).all()]
    for cat in categories:
        items = [x.serialize for x in session.query(Item)
                  .filter(Item.category_id == cat['id']).all()
                 if x.name == item]
        # if there was an item found with the name
        if len(items) > 0:
            cat['items'] = items
            categories_json.append(cat)
    close_session(session)
    json = {'category': categories_json}
    return str(json)

###############################################################
#
# Functions that provide database functionality
#
################################################################


def create_session():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def close_session(session):
    session.close()
    return


def create_user(login_session):
    session = create_session()
    qUser = User(name=login_session['username'],
                 email=login_session['email'],
                 picture=login_session['picture'])
    session.add(qUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).first()
    close_session(session)
    return user.id


def get_user_info(user_id):
    session = create_session()
    user = session.query(User).filter_by(
        id=user_id).first()
    close_session(session)
    return user


def check_user_exists(email):
    session = create_session()
    if session.query(User).filter_by(
            email=email).first():
        session = create_session()
        user = session.query(User).filter_by(
            email=email).first()
        close_session(session)
        return user.id
    else:
        close_session(session)
        return None


def make_user_if_not_exists(login_session):
    """ assign email as user id if the user exists
    else create a new user in the database """
    user_id = check_user_exists(login_session['email'])
    if user_id:
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = create_user(login_session)


def getLatestItems():
    """
    retrieves the 10 latest items
    :return:
    """
    session = create_session()
    ordered_items = session.query(Item).order_by(
        Item.id.desc()).all()
    latestitems = [(x, x.category) for x in ordered_items[0:10]]
    close_session(session)
    return latestitems


def getDescription(category_id, item_id):
    session = create_session()
    c = session.query(Category).filter(
        Category.name == category_id).first()
    item = session.query(Item).filter(
                                    Item.id == item_id,
                                    Item.category_id == c.id)\
        .first()
    item_description = item.description
    item_name = item.name
    close_session(session)
    return item_description, item_name


def getItems(category_id):
    session = create_session()
    c = session.query(Category).filter(
        Category.name == category_id).first()
    items = session.query(Item).filter_by(
                                        category_id=c.id).all()
    close_session(session)
    return items, category_id


def getCategories():
    session = create_session()
    categories = session.query(Category).all()
    close_session(session)
    return categories


###############################################################
#
# Functions that provide functionality for the Itemcatalog app
#
################################################################


@app.route('/logout/', methods=['GET'])
def gdisconnect():
    response_url = authorization.disconnect_get_session_url()
    if not authorization.check_response(response_url):
        response = authorization.do_disconnect(response_url)
        if response.status_code == 200:
            latestitems = getLatestItems()
            categories = getCategories()
            category_id = None
            state = None
            return showItems(latestitems,
                             categories,
                             category_id,
                             state)
        if response.status_code == 401:
            return response
        else:
            response
    else:
        return response_url


def disconnect_get_session_url():
    access_token = login_session.get('access_token')
    if access_token is None:
        flash('Access token not available')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = revoke_token()
        return response


def revoke_token():
    # revoke access programmatically
    response = google.post("https://accounts.google.com/o/oauth2/revoke",
                           params={'token': login_session['access_token']},
                           headers={'content-type':
                                    'application/x-www-form-urlencoded'})
    return response


@app.route('/gconnect', methods=['POST'])
def handleCallback_gconnect():
    """
    Check whether
    :return:
    """
    if authorization.validate_state_token(request):
        # Obtain authorization code
        code = request.data
        # get credentials
        response_credentials = authorization\
            .get_authorizationcode_credentials(code)
        if isinstance(response_credentials, Credentials):
            response_validity = \
                authorization.check_validity(
                    response_credentials)
            # if the app and user are verified
            # and the user is not already logged in
            if not authorization.check_response(response_validity):

                response_user = authorization.verify_access_token(
                    response_validity, response_credentials.id_token['sub'])
                # if the user and token match
                # and the client ID and the app match
                # else we return the response
                if not authorization.check_response(response_user):
                    response_app = authorization.verify_access_token_app(
                        response_validity)
                else:

                    return response_user
                if not authorization.check_response(response_app):
                    response = authorization.check_connection(
                        response_credentials.id_token['sub'])
                else:
                    return response_app
                    # if all checks passed successful
                    # return information to callback
                if not authorization.check_response(response):
                    login_session = authorization.return_login_session_info(
                        response_credentials,
                        response_credentials.id_token['sub'])
                    # make a database entry for user
                    make_user_if_not_exists(login_session)
                    return redirect(url_for('showAllCategories'))
                else:
                    return response

            else:
                return response_validity

    else:
        return response_credentials


@app.route("/login/")
def doLogin():
    """ show login page and create a anti forgery
    token for session identification """
    STATE = authorization.createToken()
    return render_template('login.html', STATE=STATE)


@app.route("/", methods=["GET"])
@app.route("/category/", methods=["GET"])
@app.route("/category/all", methods=["GET"])
@app.route("/category/<string:category_id>/", methods=["GET"])
@app.route("/category/<string:category_id>/items/", methods=["GET"])
@app.route("/category/all?STATE=<string:STATE>", methods=["GET"])
def showAllCategories(category_id=None):
    latestitems = getLatestItems()
    categories = getCategories()
    return showItems(latestitems, categories, category_id, None)


def showItems(latestitems, categories, category_id, STATE):
    """ if category id is present in the url and
    passed show only the items in the category
    else show the latest items """
    if STATE:
        return render_template('category_loggedin.html',
                               categories=categories,
                               items=[],
                               catname=None,
                               catid=None,
                               numitems=0,
                               latestitems=latestitems,
                               loggedin=True,
                               STATE=STATE)
    elif category_id:
        items, name = getItems(category_id)
        numitems = len(items)
        return render_template('category_loggedin.html',
                               categories=categories,
                               items=items,
                               catname=name,
                               catid=category_id,
                               numitems=numitems,
                               latestitems=latestitems,
                               loggedin=authorization.check_login())
    else:
        return render_template('category_loggedin.html',
                               categories=categories,
                               items=[],
                               catname=None,
                               catid=None,
                               numitems=0,
                               latestitems=latestitems,
                               loggedin=authorization.check_login())

@app.route("/category/<string:category_id>/item/<int:item_id>/description/",
           methods=["GET"])
def showDescription(category_id, item_id):
    """ render the description page for an item
    """
    item_description, item_name = getDescription(category_id, item_id)
    return render_template('descriptionitem.html',
                           description=item_description,
                           name=item_name,
                           catid=category_id,
                           item_id=item_id,
                           loggedin=authorization.check_login())


@app.route("/category/<string:category_id>/item/<int:item_id>/edit/",
           methods=["GET"])
@app.route("/items/new/", defaults={'category_id': None, 'item_id': None},
           methods=["GET"])
def editCategoryItem(category_id, item_id):
    """
    shows all  items for a given category
    :param category_id:
    :param item_id:
    :return:
    """
    if not authorization.check_login():
        return redirect(url_for('showAllCategories'))
    if request.method == 'GET':
        session = create_session()
        categories = session.query(Category).distinct(Category.name)
        # only if an item belongs to the user
        if item_id:
            c = session.query(Category)\
                            .filter(
                            Category.name == category_id)\
                            .first()
            item = session.query(Item).filter(
                                Item.user_id == login_session['user_id'],
                                Item.category_id == c.id,
                                Item.id == item_id).first()
            # if the person is the owner let him edit if not
            if item:
                return render_template('edititem.html',
                                       categories=categories)
            else:
                # if the user is not the owner
                # then render the not loggedin page
                return render_template('edititem.html',
                                       categories=categories,
                                       loggedin=authorization.check_login())
        # if it should be a new item let the person edit and own it
        elif not item_id and not category_id:
            return render_template('edititem.html',
                                   categories=categories,
                                   new=authorization.check_login())

@app.route("/category/<string:category_id>/item/<int:item_id>/edit/",
           methods=["POST"])
@app.route("/items/new/", defaults={'category_id': None, 'item_id': None},
           methods=["POST"])
def postNewItem(category_id, item_id):
    session = create_session()
    name = request.form['name']
    d = request.form['description']
    p = request.form['price']
    category = request.form['category']
    c = session.query(Category)\
        .filter(Category.name == category).first()
    # if c can't be retrieved from the category
    # then we have a wrong category name for item
    original_c = session.query(Category).filter(
        Category.name == category_id).first()
    if item_id:
        # check whether the user owns the item
        item = session.query(Item)\
            .filter(Item.user_id == login_session['user_id'],
                    Item.category_id == original_c.id,
                    Item.id == item_id).first()
    else:
        item = None
    if item:
        # checks whether any of the input is empty and
        # only assigns if input is non empty
        if name != '':
            item.name = name
        if d != '':
            item.description = d
        if p != '':
            item.price = p
        if category != '':
            item.category = c
    # if it is a new item then
    else:
        last_i = session.query(Item).order_by(
            Item.id.desc()).first()
        new_id = last_i.id + 1
        u = session.query(User)\
            .filter_by(id=login_session['user_id']).first()
        newItem = Item(
                        name=name,
                        id=new_id,
                        description=d,
                        price=p,
                        category=c,
                        user_id=login_session['user_id'],
                        user=u)
        session.add(newItem)
    session.commit()
    close_session(session)
    return redirect(url_for('showAllCategories'))

@app.route("/category/<string:category_id>/item/<int:item_id>/delete/",
           methods=["GET", "POST"])
def deleteItem(category_id, item_id):
    """ delete an item if authorized """

    if not authorization.check_login():
        return redirect(url_for('showAllCategories'))

    if request.method == 'GET':
        return render_template(
                               'deleteitem.html',
                               category_id=category_id,
                               item_id=item_id)
    else:
        session = create_session()
        c = session.query(Category)\
            .filter(Category.name == category_id).first()
        # check whether the user owns the item
        items_user = session.query(Item)\
                            .filter(
                                    Item.user_id == login_session['user_id'],
                                    Item.category == c,
                                    Item.id == item_id).all()
        if items_user:
            session.query(Item).filter(Item.id == item_id,
                                       Item.category_id == c.id)\
                                .delete()
            session.commit()
            close_session(session)
            return redirect(url_for('showAllCategories'))

        else:
            # else if the user does not own this item show all categories
            close_session(session)
            return redirect(url_for('showAllCategories'))


if __name__ == '__main__':
    app.secret_key = '_6YKl3rbWo73lUgdRmUq8iEO'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
