# -*- coding: utf-8 -*-
import os
import json

from flask import Flask
from flask.ext.testing import TestCase

from application import create_app, db

class BaseTestCase(TestCase):

  def __call__(self, result=None):
    self._pre_setup()
    super(BaseTestCase, self).__call__(result)
    self._post_teardown()

  def _pre_setup(self):
    self.app = create_app('settings_test')
    self.client = self.app.test_client()
    # self.ctx = self.app.test_request_context()
    # self.ctx.push()

  def _post_teardown(self):
    # self.ctx.pop()
    pass

  def assertRedirects(self, resp, location):
    self.assertTrue(resp.status_code in (301, 302))
    self.assertEqual(resp.location, 'http://localhost' + location)

  def assertStatus(self, resp, status_code):
    self.assertEqual(resp.status_code, status_code)


class ApiTest(BaseTestCase):

  def setUp(self):
    with self.app.app_context():
      db.create_all()

  def tearDown(self):
    with self.app.app_context():
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

  # def test_create_new_user_but_invalid_request_type(self):
  #   response = self.client.post(
  #     '/api/users',
  #     content_type='text/html'
  #   )
  #   self.assertEqual(response.status_code, 405)

  # def test_creating_new_user_successfully(self):
  #   headers = [('Content-Type', 'application/json')]
  #   data = {
  #     'username': 'test_user',
  #     'password': 'test_password'
  #   }
  #   json_data = json.dumps(data)
  #   json_data_length = len(json_data)
  #   headers.append(('Content-Length', json_data_length))

  #   response = self.client.post(
  #     '/api/users',
  #     headers=headers,
  #     data=data
  #   )
  #   print("expect 201, got %s" % response.status)
  #   self.assertEqual(response.status_code, 201)
