"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User
from flask import session

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        db.session.commit()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser.id = 9898              

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        """adding message without session will not be authorized"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True )
            # follow_redirect=True means non-redirect response is returned.

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(CURR_USER_KEY, session)
            self.assertIn(b'Access unauthorized.', resp.data)

    def test_add_invalid_user(self):
        """no access for invalid users"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 878876


            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(CURR_USER_KEY, session)
            self.assertIn(b'Access unauthorized.', resp.data)
    
    def test_message_show(self):
        """show  list of message /message/<int:message_id>"""
        
        m = Message(
            id= 939,
            text="TOO cool for school",
            user_id= self.testuser.id)

        db.session.add(m)
        db.session.commit()

       
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            m= Message.query.get(939)

            resp= c.get(f"/messages/{m.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))

    def test_add_invalid_user(self):
        """no access for invalid message id"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp= c.post('/messages/986297')
            self.assertNotEqual(resp.status_code, 200)

    def test_message_delete(self):
        """DElect message working properly"""
        m = Message(
            id= 939,
            text="TOO cool for school",
            user_id= self.testuser.id)

        db.session.add(m)
        db.session.commit()

       
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            m= Message.query.get(939)
            resp= c.post(f"/messages/{m.id}/delete")
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn(m.text, str(resp.data))

    def test_add_invalid_message(self):
        """no delete access for invalid message id"""
        m = Message(
            id= 939,
            text="TOO cool for school",
            user_id= self.testuser.id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] =self.testuser.id

            resp= c.get('/messages/7858/delete')
            self.assertNotEqual(resp.status_code, 200)
            



