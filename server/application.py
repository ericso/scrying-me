# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.restful import Api


db = SQLAlchemy()
api = Api(prefix='/api/v0')

def create_app(config_filemane):
  """Application factory
  """
  # define the WSGI application object
  flask_app = Flask(__name__)

  # configuration
  flask_app.config.from_object(config_filemane)

  # initialize the database
  db.init_app(flask_app)

  # login
  login_manager = LoginManager()
  login_manager.init_app(flask_app)

  # blueprints
  from app.users import users_blueprint
  from app.trips import trips_blueprint

  flask_app.register_blueprint(users_blueprint)
  flask_app.register_blueprint(trips_blueprint)

  # flask-restful
  from app.users import UserListAPI, UserAPI
  from app.trips import TripListAPI, TripAPI

  api.add_resource(UserListAPI, '/users', endpoint='users')
  api.add_resource(UserAPI, '/users/<int:id>', endpoint='user')

  api.add_resource(TripListAPI, '/trips', endpoint='trips')
  api.add_resource(TripAPI, '/trips/<int:id>', endpoint='trip')

  api.init_app(flask_app)

  return flask_app
