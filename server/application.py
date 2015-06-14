# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


db = SQLAlchemy()

def create_app(config_filemane):
  """Application factory
  """
  # Define the WSGI application object
  app = Flask(__name__)

  # Configuration
  app.config.from_object(config_filemane)

  # Initialize the database
  db.init_app(app)

  # Login
  login_manager = LoginManager()
  login_manager.init_app(app)

  # # Put views import after app creation to avoid circular import
  # from app import views, models

  # import blueprints
  from api.views import api_app

  # register blueprints
  app.register_blueprint(api_app)

  return app
