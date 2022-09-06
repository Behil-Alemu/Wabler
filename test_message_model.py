import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
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
    
        self.u1_id=968747
        u1.id=self.u1_id

        u1=User.query.get(self.u1_id)

        self.u1= u1
        

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Happy to be here",
            user_id=self.u1.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(m.text), 16)
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(m.text, "Happy to be here")

    def test_message_in_like(self): 
        """Test if message is in like"""
        m1 = Message(
            text="Happy to be here",
            user_id=self.u1.id
        )
        m2 = Message(
            text="or am I",
            user_id=self.u1.id
        )
        u= User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u.id=9879
        

        db.session.add_all([m1,m2,u])
        db.session.commit()

        u.likes.append(m1)
        db.session.commit()
        self.assertIn(m1,u.likes)
        self.assertIsInstance(m1.text, str)
        self.assertEqual(len(u.likes), 1)



       
