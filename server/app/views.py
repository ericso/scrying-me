from flask import g, request, jsonify, abort, url_for
from flask.ext.httpauth import HTTPBasicAuth

from app import app, db
from app.models import User

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

@app.route('/api/token')
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({'token': token.decode('ascii')})


@app.route('/api/users', methods = ['POST'])
def new_user():
  """API endpoint for creating a new user
  """
  username = request.json.get('username')
  password = request.json.get('password')

  if username is None or password is None:
    abort(400) # missing arguments
  if User.query.filter_by(username=username).first() is not None:
    abort(400) # existing user

  user = User(username=username)
  user.hash_password(password)
  db.session.add(user)
  db.session.commit()
  return jsonify({'username': user.username}), \
    201, \
    {'Location': url_for('get_user', id=user.id, _external=True)}


@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
  """API endpoint for getting a user by username
  """
  if id is None:
    abort(400) # missing arguments

  user = User.query.get(id)
  if user is None:
    abort(400) # no user found

  return jsonify({'username': user.username}), 201


@app.route('/api/resource')
@auth.login_required
def get_resource():
  return jsonify({'data': 'Hello, %s!' % g.user.username})
