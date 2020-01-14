from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine("postgresql+psycopg2://<user>:<password>@127.0.0.1:5432/itemcatalog")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
User1 = User(name="Komischer Typ", email="komischertyp@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="Komischer Typ 2", email="komischertyp2@udacity.com",
             picture='https://pbs.twimg.com/profile_images/26731170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()


category1 = Category(user_id=2, name="Baseball")

session.add(category1)
session.commit()

Item2 = Item(user_id=2, name="hat", description="covers the head",
                     price="$7.50", category=category1)

session.add(Item2)
session.commit()


Item1 = Item(user_id=2, name="Bat", description="to beat the ball",
                     price="$30.99", category=category1)

session.add(Item1)
session.commit()

Item2 = Item(user_id=1, name="ball", description="ball to throw",
                     price="$15.40", category=category1)

session.add(Item2)
session.commit()

category2 = Category(user_id=2, name="Basketball")

session.add(category2)
session.commit()

Item2 = Item(user_id=1, name="hat", description="covers the head",
                     price="$7.50", category=category2)

session.add(Item2)
session.commit()


Item1 = Item(user_id=1, name="shirt", description="covers the chest",
                     price="$30.99", category=category2)

session.add(Item1)
session.commit()

Item3 = Item(user_id=1, name="ball", description="ball to throw",
                     price="$45.40", category=category2)

session.add(Item3)
session.commit()

Item4 = Item(user_id=1, name="trouser", description="covers the legs",
                     price="$45.40", category=category2)

session.add(Item4)
session.commit()



print("added  items!")
