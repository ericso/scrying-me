# -*- coding: utf-8 -*-
import json

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
    test_user = User(username=test_username)
    test_user.hash_password(test_password)
    db.session.add(test_user)
    db.session.commit()

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

