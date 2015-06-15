# -*- coding: utf-8 -*-
import json
from base64 import b64encode

from flask import Flask
from flask.ext.testing import TestCase

from application import create_app, db
from api.models import User
from common.tests import BaseTestCase


class ApiTest(BaseTestCase):

  def setUp(self):
    with self.app.app_context():
      db.create_all()

  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

  def create_user(self, username, password):
    """Creates a user with hashed password in the database

    :return: user object
    """
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return user

  def create_basic_auth_header(self, username, password):
    """
    :return: Basic auth header entry
    """
    return {
      'Authorization': 'Basic %s' % b64encode("{0}:{1}".format(username, password))
    }

  ### Tests ###
  def test_create_new_user_but_missing_arguments(self):
    response = self.client.post(
      '/api/users',
      content_type='application/json'
    )
    self.assertEqual(response.status_code, 400)

  def test_create_new_user_but_invalid_request_type(self):
    response = self.client.post(
      '/api/users',
      content_type='text/html'
    )
    self.assertEqual(response.status_code, 405)

  def test_creating_new_user_successfully(self):
    headers = {
      'Content-Type': 'application/json'
    }
    data = dict(username='test_user', password='test_password')
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    response = self.client.post(
      '/api/users',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 201)

  def test_create_new_user_but_user_exists(self):
    # Create user
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = self.create_user(username=test_username, password=test_password)

    # Try to create the same user by sending request
    headers = {
      'Content-Type': 'application/json'
    }
    data = dict(username=test_username, password=test_password)
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    response = self.client.post(
      '/api/users',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 403)

  def test_get_auth_token_successfully(self):
    # Create the user to request a token
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = self.create_user(username=test_username, password=test_password)

    headers = self.create_basic_auth_header(
      username=test_username,
      password=test_password
    )
    response = self.client.get(
      '/api/token',
      headers=headers
    )
    data = json.loads(response.data)
    self.assertIn('token', data.keys())

  def test_get_auth_token_failure(self):
    # Create the user to request a token
    test_username = 'test_user'
    test_password = 'test_password'
    test_user = self.create_user(username=test_username, password=test_password)

    headers = self.create_basic_auth_header(
      username='wrongusername',
      password='wrongpassword'
    )
    response = self.client.get(
      '/api/token',
      headers=headers
    )
    self.assertEqual(response.status_code, 401)
