import pytest
import os
from app import create_app
from extensions import db, bcrypt
from models import User, ParcelOrder


os.environ['TESTING'] = 'True'




@pytest.fixture
def app():
   app = create_app({
       'TESTING': True,
       'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
       'SQLALCHEMY_TRACK_MODIFICATIONS': False,
       'JWT_SECRET_KEY': 'test-jwt-secret',
       'WTF_CSRF_ENABLED': False
   })
  
   with app.app_context():
       db.create_all()
       yield app
       db.drop_all()




@pytest.fixture
def client(app):