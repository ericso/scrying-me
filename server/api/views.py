# -*- coding: utf-8 -*-
import json

from flask import Blueprint, current_app
from flask import jsonify, url_for
from flask import g, request, Response
from flask.ext.httpauth import HTTPBasicAuth

from application import db
from api.models import User


api_app = Blueprint('api_app', __name__)

auth = HTTPBasicAuth()

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

@api_app.route('/api/token')
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({'token': token.decode('ascii')})


@api_app.route('/api/users', methods=['POST'])
def new_user():
  """API endpoint for creating a new user

  :return: status code 400 BAD REQUEST - missing username or password
  :return: status code 403 FORBIDDEN - user already exists
  :return: status code 405 METHOD NOT ALLOWED - invalid JSON or request type
  :return: status code 201 CREATED - successful submission
  """
  if request.headers['content-type'] == 'application/json':
    # return Response(status=300)
    # try:
    #   username = request.json.get('username')
    #   password = request.json.get('password')
    # except ValueError:
    #   return Response(status=300)

    # try:
    #   # data = json.loads(request.get_json())
    #   data = request.get_json()
    # except ValueError:
    #   return Response(status=405)
    # else:
    #   username = data.get('username')
    #   password = data.get('password')

    # data = json.loads(request.get_json())
    data = request.get_json()
    username = data['username']
    password = data['password']


    # if username is None or password is None:
    #   return Response(status=400) # missing arguments
    if User.query.filter_by(username=username).first() is not None:
      return Response(status=403) # existing user

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), \
      201, \
      {'Location': url_for('api_app.get_user', id=user.id, _external=True)}
  else:
    return Response(status=405) # invalid request type


@api_app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
  """API endpoint for getting a user by username
  """
  if id is None:
    abort(400) # missing arguments

  user = User.query.get(id)
  if user is None:
    abort(400) # no user found

  return jsonify({'username': user.username}), 201


@api_app.route('/api/resource')
@auth.login_required
def get_resource():
  return jsonify({'data': 'Hello, %s!' % g.user.username})
