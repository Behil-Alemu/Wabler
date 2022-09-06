"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from psycopg2 import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()
        db.create_all()

        u1=User.signup(username="user1",
            email="email1@gmail.com",
            password="hashed_pwd",
            image_url=None
        )
        u1_id=968747
        u1.id=u1_id

        u2=User.signup(username="user2",
            email="email2@gmail.com",
            password="hashed_pwd2",
            image_url=None
        )
        u2_id=986794
        u2.id=u2_id

        db.session.commit()


        u1=User.query.get(u1_id)
        u2=User.query.get(u2_id)

        self.u1= u1
        self.u2= u2

        self.u1_id=u1_id
        self.u2_id=u2_id


        self.client = app.test_client()


    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """id the __repr__ working properly"""
        repr(self.id)

    def test_user_follow(self):
        """What to expect when user1(1)follows user2(u2)"""
        self.u2.followers.append(self.u1)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)

        self.assertEqual(self.u1.following[0].id,self.u2.id )
        self.assertEqual(self.u2.followers[0].id,self.u1.id )

        
    def test_is_following(self):
        """successfully detect when user1 is following user2"""
        self.u2.followers.append(self.u1)
        db.session.commit()
        self.assertTrue(self.u1.following[0].id,self.u2.id )
        self.assertFalse(self.u2.is_following(self.u1))
        self.assertTrue(self.u1.is_following(self.u2))



    def test_is_followed(self):
        """successfully detect when user2 is followed by  user1"""
        self.u2.followers.append(self.u1)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_user_signup(self):
        """check valid credentials place when signing up"""
        test_user= User.signup("username","useremail@gmail.com", "hashed_pwd", None)
        user_id= 93427
        test_user.id = user_id
        db.session.commit()

        user1 = User.query.get(user_id)
        self.assertEqual(user1.username, "username")
        self.assertEqual(user1.email, "useremail@gmail.com")
        self.assertNotEqual(user1.password, "hashed_pwd")
        self.assertNotEqual(user1.username, None)


    def test_invalid_pwds(self):
        """Test for invaild password"""
        with self.assertRaises(ValueError) as context:
            User.signup("username","useremail@gmail.com", "", None)
        with self.assertRaises(ValueError) as context:
            User.signup("username","useremail@gmail.com", None, None)

    def test_invalid_username(self):
        """test for invalid usernames"""
        test_user= User.signup(None,"useremail@gmail.com", "hashed_pwd", None)
        user_id= 93427
        test_user.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        """check for invalid emails"""
        test_user= User.signup("Username",None, "hashed_pwd", None)
        user_id= 93427
        test_user.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_login(self):
        """Test authenticate"""
        user = User.authenticate(self.u1.username,'hashed_pwd')
        self.assertEqual(user.username, "user1")
        self.assertEqual(user.id, self.u1_id)
        self.assertEqual(user.password, self.u1.password)
        self.assertFalse(User.authenticate('NotUser', self.u1.password))
        self.assertTrue(User.authenticate(self.u1.username, "hashed_pwd"))






        
        
       





