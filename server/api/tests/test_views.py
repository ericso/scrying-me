# -*- coding: utf-8 -*-
import json
from base64 import b64encode
from datetime import date

from flask import Flask
from flask.ext.testing import TestCase

from application import create_app, db
from api.models import User, Trip
from api.serializers import default_json_serializer
from common.tests import BaseTestCase


class UsersTest(BaseTestCase):

  def setUp(self):
    with self.app.app_context():
      db.create_all()

  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

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
  def create_basic_auth_header(username, password):
    """
    :return: Basic auth header entry
    """
    return {
      'Authorization': 'Basic %s' % b64encode("{0}:{1}".format(username, password))
    }

  ### Tests ###
  def test_get_user_by_id(self):
    # Create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(username=test_username, password=test_password)

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

  # def test_get_user_by_username(self):
  #   # Create user
  #   test_username = 'test_user'
  #   test_password = 'test_password'
  #   test_user = UsersTest.create_user(username=test_username, password=test_password)

  #   response = self.client.get(
  #     '/api/v0/users/%s' % (test_username,)
  #   )
  #   self.assertEqual(response.status_code, 200)
  #   user = json.loads(response.data)
  #   self.assertEqual(user['username'], test_username)

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
    self.assertEqual(response.status_code, 405)

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

  def test_create_new_user_but_user_exists(self):
    # Create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(username=test_username, password=test_password)

    # Try to create the same user by sending request
    headers = {
      'Content-Type': 'application/json'
    }
    data = dict(username=test_username, password=test_password)
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    response = self.client.post(
      '/api/v0/users',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 403)

  def test_get_auth_token_successfully(self):
    # Create the user to request a token
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(username=test_username, password=test_password)

    headers = UsersTest.create_basic_auth_header(
      username=test_username,
      password=test_password
    )
    response = self.client.get(
      '/api/v0/token',
      headers=headers
    )
    data = json.loads(response.data)
    self.assertIn('token', data.keys())

  def test_get_auth_token_failure(self):
    # Create the user to request a token
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = UsersTest.create_user(username=test_username, password=test_password)

    headers = UsersTest.create_basic_auth_header(
      username='wrongusername',
      password='wrongpassword'
    )
    response = self.client.get(
      '/api/v0/token',
      headers=headers
    )
    self.assertEqual(response.status_code, 401)


class ApiTest(BaseTestCase):

  def setUp(self):
    """Creates a user and saves the auth token
    """
    with self.app.app_context():
      db.create_all()

    # create user
    self.test_username = 'test_user'
    self.test_password = 'test_password'
    self.test_user = UsersTest.create_user(
      username=self.test_username,
      password=self.test_password
    )
    # create auth header
    self.auth_headers = UsersTest.create_basic_auth_header(
      username=self.test_username,
      password=self.test_password
    )
    # get auth token
    response = self.client.get(
      '/api/v0/token',
      headers=self.auth_headers
    )
    self.token = json.loads(response.data)['token']

  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

  @staticmethod
  def create_trip(name, start, end):
    """Creates a trip

    :return: trip object
    """
    trip = Trip(name=name, start=start, end=end)
    db.session.add(trip)
    db.session.commit()
    return trip

  def get_resource_with_username_and_password(self, resource):
    # self.auth_headers is already prepared the Authorization header
    response = self.client.get(
      '/api/v0/%s' % resource,
      headers=self.auth_headers
    )
    return response

  def get_resource_with_auth_token(self, resource):
    # self.token has been requested via the test setup
    headers = UsersTest.create_basic_auth_header(
      username=self.token,
      password=''
    )
    response = self.client.get(
      '/api/v0/%s' % resource,
      headers=headers
    )
    return response

  ### Tests ###
  def test_get_resource_with_username_and_password(self):
    resource='resources'
    response = self.get_resource_with_username_and_password(resource)
    data = json.loads(response.data)
    self.assertEqual(response.status_code, 200)
    self.assertIn('data', data.keys())

  def test_get_resource_with_username_and_password(self):
    resource='resources'
    response = self.get_resource_with_auth_token(resource)
    data = json.loads(response.data)
    self.assertEqual(response.status_code, 200)
    self.assertIn('data', data.keys())

  def test_create_new_trip_successfully(self):
    headers = {
      'Content-Type': 'application/json'
    }
    # Have the trip start on Jan 1, 1970 and end on Jan 31, 1970
    date_start = date(year=1970, month=1, day=1)
    date_end = date(year=1970, month=1, day=31)
    data = dict(name='test_trip', start=date_start, end=date_end)
    json_data = json.dumps(data, default=default_json_serializer)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    # Add authorization headers
    headers.update(self.auth_headers)

    response = self.client.post(
      '/api/v0/trips',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 201)

  def test_get_trip_by_id(self):
    # Create a trip
    trip_name = "My Trip"
    trip_start = date(year=1970, month=1, day=1)
    trip_end = date(year=1970, month=1, day=31)
    test_trip = ApiTest.create_trip(name=trip_name, start=trip_start, end=trip_end)

    response = self.client.get(
      '/api/v0/trips/%s' % (test_trip.id,),
      headers=self.auth_headers
    )
    self.assertEqual(response.status_code, 200)
    return_trip = json.loads(response.data)
    self.assertEqual(return_trip['trip'], trip_name)
