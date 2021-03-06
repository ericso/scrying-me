# -*- coding: utf-8 -*-
import json
from base64 import b64encode
from copy import copy

from application import db
from app.models import User
from common.tests import BaseTestCase
from common.util import rand_string_gen

from application import create_app


class UsersTest(BaseTestCase):

  def create_app(self):
    return create_app('settings_test')

  def setUp(self):
    with self.app.app_context():
      db.create_all()

  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

  def get_token_for_user(self, username, password, failure=False):
    """Shortcut method for creating a user in the test db
    and requesting an auth token via the API
    """
    test_user = UsersTest.create_user(
      username=username,
      password=password
    )

    if failure:
      headers = UsersTest.create_basic_auth_header(
        username=username,
        password='thisisincorrectpassword'
      )
    else:
      headers = UsersTest.create_basic_auth_header(
        username=username,
        password=password
      )

    response = self.client.get(
      '/api/v0/token',
      headers=headers
    )
    return response

  def authorize_user(self, username, password, failure=False):
    """Shortcut method for creating a user in the test db
    and authenticating the user via the API
    """
    test_user = UsersTest.create_user(
      username=username,
      password=password
    )

    headers = {
      'Content-Type': 'application/json'
    }
    if failure:
      data = dict(username=username, password='thisisincorrectpassword')
    else:
      data = dict(username=username, password=password)
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    response = self.client.post(
      '/api/v0/authenticate',
      headers=headers,
      data=json_data
    )
    return response

  @staticmethod
  def create_user(username, password):
    """Creates a user with hashed password in the database

    :return: user object
    """
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return user

  @staticmethod
  def generate_test_users(n=1):
    """Returns a list of n test users
    """
    rv = list()
    for i in xrange(0, n):
      rv.append({'username': rand_string_gen(), 'password': rand_string_gen()})
    return rv

  @staticmethod
  def create_basic_auth_header(username, password):
    """
    :return: Basic auth header entry
    """
    return {
      'Authorization': 'Basic %s' % b64encode("{0}:{1}".format(username, password))
    }


  ### Tests ###
  def test_get_all_users(self):
    num_users = 5
    users = UsersTest.generate_test_users(num_users)
    for user in users:
      UsersTest.create_user(user['username'], user['password'])

    auth_headers = UsersTest.create_basic_auth_header(
      username=users[0]['username'],
      password=users[0]['password']
    )
    response = self.client.get(
      '/api/v0/users',
      headers=auth_headers
    )
    self.assertStatus(response, 200)
    data = json.loads(response.data)
    users = data['data']
    self.assertEqual(len(users), num_users)

  def test_get_user_by_id(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )

    auth_headers = UsersTest.create_basic_auth_header(
      username=test_username,
      password=test_password
    )
    response = self.client.get(
      '/api/v0/users/%s' % (test_user.id,),
      headers=auth_headers
    )
    self.assertEqual(response.status_code, 200)
    user = json.loads(response.data)
    self.assertEqual(user['username'], test_username)

  def test_get_user_not_found(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )
    # create the auth header
    auth_headers = UsersTest.create_basic_auth_header(
      username=test_username,
      password=test_password
    )
    response = self.client.get(
      '/api/v0/users/999', # this user doesn't exist
      headers=auth_headers
    )
    self.assertEqual(response.status_code, 404)
    # self.assertEqual(response.message, "User not found")

  def test_get_user_by_username(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )

    auth_headers = UsersTest.create_basic_auth_header(
      username=test_username,
      password=test_password
    )
    response = self.client.get(
      '/api/v0/users/%s' % (test_username,),
      headers=auth_headers
    )
    self.assertStatus(response, 200)
    user = json.loads(response.data)
    self.assertEqual(user['username'], test_username)


  def test_create_new_user_but_missing_arguments(self):
    response = self.client.post(
      '/api/v0/users',
      content_type='application/json'
    )
    self.assertEqual(response.status_code, 400)

  def test_create_new_user_but_invalid_request_type(self):
    response = self.client.post(
      '/api/v0/users',
      content_type='text/html'
    )
    self.assertEqual(response.status_code, 400)

  def test_create_new_user_successfully(self):
    headers = {
      'Content-Type': 'application/json'
    }
    data = dict(username='test_user', password='test_password')
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    response = self.client.post(
      '/api/v0/users',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 201)
    res_data = json.loads(response.data)
    self.assertEqual(res_data['user']['username'], data['username'])
    self.assertIn('uri', res_data['user'].keys())

  def test_create_new_user_but_user_exists(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )

    # try to create the same user by sending request
    headers = {
      'Content-Type': 'application/json'
    }
    data = dict(username=test_username, password=test_password)
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] = json_data_length

    response = self.client.post(
      '/api/v0/users',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 403)

  def test_update_user_password(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )
    headers = dict()

    # create the auth header
    headers.update(
      UsersTest.create_basic_auth_header(
        username=test_username,
        password=test_password
      )
    )

    # create the json payload
    new_password = 'new_password'
    data = dict(password=new_password)
    json_data = json.dumps(data)
    json_data_length = len(json_data)

    # update the content headers
    headers.update({
      'Content-Type': 'application/json',
      'Content-Length': json_data_length
    })

    response = self.client.put(
      '/api/v0/users/%s' % (test_user.id,),
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 201)

  def test_delete_user(self):
    # create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(
      username=test_username,
      password=test_password
    )
    test_user_id = copy(test_user.id)
    headers = dict()

    # create the auth header
    headers.update(
      UsersTest.create_basic_auth_header(
        username=test_username,
        password=test_password
      )
    )
    response = self.client.delete(
      '/api/v0/users/%s' % (test_user_id,),
      headers=headers
    )
    self.assertEqual(response.status_code, 202)

    # try querying for the user should return 401 UNAUTHORIZED
    response = self.client.get(
      '/api/v0/users/%s' % (test_user_id,),
      headers=headers
    )
    self.assertEqual(response.status_code, 401)

  def test_authenticate_user_successfully(self):
    response = self.authorize_user('test_user', 'test_password')
    self.assertEqual(response.status_code, 201)

  def test_authenticate_user_response_contains_cors_headers(self):
    response = self.authorize_user('test_user', 'test_password')
    self.assertCORSHeaders(response)

  def test_authenticate_user_unsuccessfully(self):
    response = self.authorize_user('test_user', 'test_password', failure=True)
    self.assertEqual(response.status_code, 403)
