# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.errorhandler import ErrorHandler

db = SQLAlchemy()
errorhandler = ErrorHandler()

def create_app(config_filemane):
  """Application factory
  """
  # define the WSGI application object
  app = Flask(__name__)

  # configuration
  app.config.from_object(config_filemane)

  # initialize the database
  db.init_app(app)

  # login
  login_manager = LoginManager()
  login_manager.init_app(app)

  # import blueprints
  from api.views import users_app
  from api.views import trips_app

  # register blueprints
  app.register_blueprint(users_app)
  app.register_blueprint(trips_app)

  # error handling
  errorhandler.init_app(app)

  return app
