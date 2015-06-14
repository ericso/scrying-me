from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


def create_app(config_filemane='config'):
  """Application factory
  """
  # Define the WSGI application object
  app = Flask(__name__)

  # Configurations
  # app.config.from_object('config')
  app.config.from_pyfile(config_filemane)

  # Define the database object which is imported
  # by modules and controllers
  db = SQLAlchemy(app)

  # Login
  login_manager = LoginManager()
  login_manager.init_app(app)

  # Put views import after app creation to avoid circular import
  from app import views, models

  return app
