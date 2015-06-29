# -*- coding: utf-8 -*-
import json
from datetime import datetime

from flask import Blueprint, current_app
from flask import jsonify, url_for
from flask import g, abort, request, Response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse, fields, marshal

from application import db, api
from app.models import User, Trip
from app.serializers import user_json_serializer
from common.http import add_cors_headers


users_blueprint = Blueprint('users_blueprint', __name__)

auth = HTTPBasicAuth()

# TODO(eso) decide if Blueprints are necessary here
# @users_blueprint.after_request
# def after_request(response):
#   return add_cors_headers(response)

# TODO(eso) refactor the authenticate into the user API class
@users_blueprint.route('/api/v0/authenticate', methods=['POST'])
def authenticate_user():
  """API endpoint for authenticating a new user

  :return: status code 400 BAD REQUEST - missing application/json header
  :return: status code 400 BAD REQUEST - missing username or password
  :return: status code 403 FORBIDDEN - user not authenticated
  :return: status code 201 CREATED - successful submission
  """
  if request.headers['content-type'] == 'application/json':
    print(request)
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

    return jsonify({'username': username, 'success': True}), 201
  else:
    print("invalid request type, no json")
    return Response(status=400) # invalid request type


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


user_fields = {
  'username': fields.String,
  'uri': fields.Url('user')
}

class UserListAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('username',
                               type=str,
                               required=True,
                               help="No username provided",
                               location='json')
    self.reqparse.add_argument('password',
                               type=str,
                               required=True,
                               help="No password provided",
                               location='json')
    super(UserListAPI, self).__init__()

  @auth.login_required
  def get(self):
    users = User.query.all()
    rv = list()
    for user in users:
      rv.append(user_json_serializer(user))
    return {'data': rv}, 200

  def post(self):
    if request.headers['content-type'] == 'application/json':
      args = self.reqparse.parse_args()

      username = args['username']
      password = args['password']
      if User.query.filter_by(username=username).first() is not None:
        return Response(status=403) # existing user

      user = User(username=username)
      user.hash_password(password)
      db.session.add(user)
      db.session.commit()
      return {'user': marshal(user, user_fields)}, 201
    else:
      return Response(status=400) # invalid request type


class UserAPI(Resource):

  decorators = [auth.login_required]

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('password',
                               type=str,
                               required=True,
                               help="No password provided",
                               location='json')
    super(UserAPI, self).__init__()

  def get(self, id):
    user = User.query.get(id)
    if user is None:
      abort(404)
    return {'username': user.username}, 200

  def put(self, id):
    if request.headers['content-type'] == 'application/json':
      args = self.reqparse.parse_args()
      password = args['password']
      user = User.query.get(id)
      if user is None:
        abort(404)

      # TODO(eso) abort if hashed password matches old password
      user.hash_password(password)
      db.session.add(user)
      db.session.commit()
      return {'user': marshal(user, user_fields)}, 201
    else:
      return Response(status=400) # invalid request type

  # TODO(eso) this api route should be protected by a consent token from the client
  # TODO(eso) implement active/inactive users
  def delete(self, id):
    user = User.query.get(id)
    if user is None:
      abort(404)
    db.session.delete(user)
    db.session.commit()
    return Response(status=202)

def add_user_resources():
  """Call this function in Flask application.py file to add these resources
  after the API object has been initialized with the WSGI app object
  """
  api.add_resource(UserListAPI, '/users', endpoint='users')
  api.add_resource(UserAPI, '/users/<int:id>', endpoint='user')
