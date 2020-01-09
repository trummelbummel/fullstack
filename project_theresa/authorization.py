from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from flask import session as login_session
from flask import request, make_response, flash

from flask import Response

import ast
import inspect
import httplib2
import json
import requests
import random
import string

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Menu Application"


def check_login():
    """
    returns false if user is not logged in
    :return:
    """
    if not login_session.get('username'):
        return False
    else:
        return True

def validate_state_token(request):
    """
    :return: response
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'session state not matching request state token'), 401)
        flash('session state not matching request state token')
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return True

def get_authorizationcode_credentials(code):
    """

    :return:
    """
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        return credentials
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

def check_validity(credentials):
    # Check that the access token is valid.

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    result = json.loads(requests.get(url).text)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(
            result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        flash("Credentials ok")
        return result

def check_response(result):
    """ checks whether the response is expected or
    an error response """
    if isinstance(result, Response):
        return True
    else:
        flash('continue flow')
        return False

def createToken():
    """ show login page and create a anti forgery
    token for session identification """
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session["state"] = state
    return state

def verify_access_token(result, gplus_id):
    """
    Verify that the token is used for the correct user
    :param result:
    :return:
    """

    if result.get('user_id') != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID.")
            , 401)
        flash('tokens user ID doesnt match given user ID')
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        True

def verify_access_token_app(result):
    """
    Verify that the client ID is valid
    :param result:
    :return:
    """
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Client ID doesn't match app ID")
            , 401)
        flash("Client ID doesn't match app ID")
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        True

def check_connection(gplus_id):
    """ check whether login session already exists """
    stored_access_token = login_session.get('state')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("User is already connected"),
                                 200)
        flash("User already connected")
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        True

def return_login_session_info(credentials, gplus_id):
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    userinfo = requests.get(userinfo_url, params=params)
    info = userinfo.json()
    login_session['username'] = info['name']
    login_session['picture'] = info['picture']
    login_session['email'] = info['email']
    flash("you are now logged in as %s" % login_session['username'])
    return login_session

def disconnect_get_session_url():
    access_token = login_session.get('access_token')
    if access_token is None:
        flash('Access token not available')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = revoke_token()
        return response

def revoke_token():
    response = requests.post('https://accounts.google.com/o/oauth2/revoke',
                  params={'token': login_session['access_token']},
                  headers={'content-type': 'application/x-www-form-urlencoded'})
    return response

def do_disconnect(response):
    if response.status_code == 200:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    if response.status_code == 401:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(' disconnected unauthorized.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

