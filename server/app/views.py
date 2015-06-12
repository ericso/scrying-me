from flask import request, jsonify, abort, url_for

from app import app, db
from app.models import User

@app.route('/api/users', methods = ['POST'])
def new_user():
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
  # return jsonify({'username': user.username}), \
  #   201, \
  #   {'Location': url_for('get_user', id=user.id, _external=True)}

  return jsonify({'username': user.username}), 201
