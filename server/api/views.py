# -*- coding: utf-8 -*-
import json
from datetime import datetime

from flask import Blueprint, current_app
from flask import jsonify, url_for
from flask import g, request, Response
from flask.ext.httpauth import HTTPBasicAuth

from application import db
from api.models import User, Trip


users_app = Blueprint('users_app', __name__)
api_app = Blueprint('api_app', __name__)

auth = HTTPBasicAuth()

@users_app.after_request
@api_app.after_request
def add_headers(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


@auth.verify_password
def verify_password(username_or_token, password):
  """Callback for Flask-HTTPAuth to verify given password for username
      or auth token
  If password (for username) or auth token is verified,
   the user object is stored on g.user global
  """
  # try to authenticate by token first
  user = User.verify_auth_token(username_or_token)
  if not user:
    # try to authenticate with username/password
    user = User.query.filter_by(username=username_or_token).first()
    if not user or not user.verify_password(password):
      return False
  g.user = user
  return True

@users_app.route('/api/v0/users', methods=['POST'])
def new_user():
  """API endpoint for creating a new user

  :return: status code 400 BAD REQUEST - missing username or password
  :return: status code 403 FORBIDDEN - user already exists
  :return: status code 405 METHOD NOT ALLOWED - invalid JSON or request type
  :return: status code 201 CREATED - successful submission
  """
  if request.headers['content-type'] == 'application/json':
    data = request.get_json()
    if data:
      username = data['username']
      password = data['password']
    else:
      return Response(status=400) # no JSON to parse

    if username is None or password is None:
      return Response(status=400) # missing arguments
    if User.query.filter_by(username=username).first() is not None:
      return Response(status=403) # existing user

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), \
      201, \
      {'Location': url_for('users_app.get_user', id=user.id, _external=True)}
  else:
    return Response(status=405) # invalid request type

@users_app.route('/api/v0/authenticate', methods=['POST'])
def authenticate_user():
  """API endpoint for authenticating a new user

  :return: status code 400 BAD REQUEST - missing username or password
  :return: status code 403 FORBIDDEN - user not authenticated
  :return: status code 405 METHOD NOT ALLOWED - invalid JSON or request type
  :return: status code 201 CREATED - successful submission
  """
  if request.headers['content-type'] == 'application/json':
    data = request.get_json()
    if data:
      username = data['username']
      password = data['password']
    else:
      return Response(status=400) # no JSON to parse

    if username is None or password is None:
      return Response(status=400) # missing arguments

    if not verify_password(username, password):
      return Response(status=403) # User not authenticated

    return Response(status=201)
  else:
    return Response(status=405) # invalid request type

@users_app.route('/api/v0/users/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
  """API endpoint for getting a user by id
  """
  if id is None:
    abort(400) # missing arguments

  user = User.query.get(id)
  if user is None:
    abort(400) # no user found

  return jsonify({'username': user.username}), 200

# @users_app.route('/api/v0/users/<username>', methods=['GET'])
# def get_user(username):
#   """API endpoint for getting a user by username
#   """
#   if username is None:
#     abort(400) # missing arguments

#   user = User.query.filter(username==username).first()
#   if user is None:
#     abort(400) # no user found

#   return jsonify({'username': user.username}), 200


@users_app.route('/api/v0/token')
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({'token': token.decode('ascii')})


@api_app.route('/api/v0/resources')
@auth.login_required
def get_resource():
  return jsonify({'data': 'Hello, %s!' % g.user.username}), 200


@api_app.route('/api/v0/trips', methods=['POST'])
def new_trip():
  """API endpoint for creating a new trip

  :return: status code 400 BAD REQUEST - missing arguments
  :return: status code 401 NOT AUTHROIZED - invalid credentials
  :return: status code 405 METHOD NOT ALLOWED - invalid JSON or request type
  :return: status code 201 CREATED - successful submission
  """
  if request.headers['content-type'] == 'application/json':
    data = request.get_json()
    if data:
      name = data['name']
      start = datetime.fromtimestamp(data['start'])
      end = datetime.fromtimestamp(data['end'])
    else:
      return Response(status=400) # no JSON to parse

    if name is None or start is None or end is None:
      return Response(status=400) # missing arguments

    trip = Trip(name=name, start=start, end=end)
    db.session.add(trip)
    db.session.commit()
    return jsonify({'trip': trip.name}), \
      201, \
      {'Location': url_for('api_app.get_trip', id=trip.id, _external=True)}
  else:
    return Response(status=405) # invalid request type

@api_app.route('/api/v0/trips/<int:id>', methods=['GET'])
@auth.login_required
def get_trip(id):
  """API endpoint for getting a trip by id
  """
  if id is None:
    abort(400) # missing arguments

  trip = Trip.query.get(id)
  if trip is None:
    abort(400) # no trip found

  return jsonify({'trip': trip.name}), 200
