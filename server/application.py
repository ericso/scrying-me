# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
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

  # blueprints
  from app.users import users_blueprint
  from app.trips import trips_blueprint

  flask_app.register_blueprint(users_blueprint)
  flask_app.register_blueprint(trips_blueprint)

  # flask-restful
  from app.users import add_user_resources
  from app.trips import add_trip_resources

  api.init_app(flask_app)
  add_user_resources()
  add_trip_resources()


  return flask_app
