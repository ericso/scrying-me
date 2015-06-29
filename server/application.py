# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.cors import CORS

db = SQLAlchemy()
api = Api(prefix='/api/v0')
cors = CORS(resources={r'/api/v0/*': {'origins': '*'}})

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

  # TODO(eso)
  """
  The proper way to add resources to the api is to do it before we call init_app()
  However, in doing so our tests fail with the error:
    AssertionError: View function mapping is overwriting an existing endpoint function: users
    need to figure out why we're getting these AssertionErrors in the tests
  """
  # before init_app:
  # single test fails (nosetests app.tests.test_users:UsersTest.test_get_all_users)
  # nosetest fails
  # curl passes
  # API request via AngularJS successful
  add_user_resources()
  add_trip_resources()

  api.init_app(flask_app)

  # after init_app:
  # single test passes (nosetests app.tests.test_users:UsersTest.test_get_all_users)
  # running nosetests fails
  # API request via curl returns 404
  # API request via AngularJS returns 404 on options request
  # add_user_resources()
  # add_trip_resources()

  # CORS handling
  # from common.http import add_cors_headers
  # @flask_app.after_request
  # def after_request(response):
  #   return add_cors_headers(response)
  cors.init_app(flask_app)

  return flask_app
