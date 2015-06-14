import os
import json
import unittest

from flask import Flask
from flask.ext.testing import TestCase

from app import app, db


class ApiTest(TestCase):

  # Define the test directory
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'testing.db')
  TESTING = True

  def create_app(self):
    app.config['TESTING'] = True
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    return app

  def setUp(self):
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()

  def test_create_new_user_but_missing_arguments(self):
    response = self.client.post(
      '/api/users',
      content_type='application/json'
    )
    self.assertEqual(response.status_code, 405)

  # def test_create_new_user_but_user_exists(self):
  #   self.fail("write test")

  def test_create_new_user_but_invalid_request_type(self):
    response = self.client.post(
      '/api/users',
      content_type='text/html'
    )
    self.assertEqual(response.status_code, 405)

  def test_creating_new_user_successfully(self):
    headers = [('Content-Type', 'application/json')]
    data = {
      'username': 'test_user',
      'password': 'test_password'
    }
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers.append(('Content-Length', json_data_length))

    response = self.client.post(
      '/api/users',
      headers=headers,
      data=data
    )
    print("expect 201, got %s" % response.status)
    self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
  unittest.main()
