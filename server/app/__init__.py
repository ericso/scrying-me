from flask import Flask, render_template
  from flask.ext.sqlalchemy import SQLAlchemy

  # Define the WSGI application object
  app = Flask(__name__)

  # Configurations
  app.config.from_object('config')

  # Define the database object which is imported
  # by modules and controllers
  db = SQLAlchemy(app)


  # Put views import after app creation to avoid circular import
  from app import views, models
  
