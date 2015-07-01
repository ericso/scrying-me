# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.cors import CORS

db = SQLAlchemy()

def create_app(config_filemane):
  """Application factory
  """
  # define the WSGI application object
  flask_app = Flask(__name__)

  # configuration
  flask_app.config.from_object(config_filemane)

  # initialize the database
  db.init_app(flask_app)

  # blueprints
  from app.users import users_blueprint
  from app.trips import trips_blueprint
  flask_app.register_blueprint(users_blueprint)
  flask_app.register_blueprint(trips_blueprint)

  # flask-restful
  from app.users import UserListAPI, UserAPI
  from app.trips import TripListAPI, TripAPI
  api = Api(prefix='/api/v0')
  api.add_resource(UserListAPI, '/users', endpoint='users')
  api.add_resource(UserAPI, '/users/<id>', endpoint='user')
  api.add_resource(TripListAPI, '/trips', endpoint='trips')
  api.add_resource(TripAPI, '/trips/<int:id>', endpoint='trip')
  api.init_app(flask_app)

  cors = CORS(resources={r'/api/v0/*': {'origins': '*'}})
  cors.init_app(flask_app)

  return flask_app
