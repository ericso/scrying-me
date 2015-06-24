# -*- coding: utf-8 -*-
import json
from base64 import b64encode
from datetime import date

from flask import Flask
from flask.ext.testing import TestCase

from application import db
from api.models import Trip
from api.serializers import default_json_serializer
from api.tests.test_users import UsersTest
from common.tests import BaseTestCase


class TripsTest(BaseTestCase):

  def setUp(self):
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
    # # get auth token
    # response = self.client.get(
    #   '/api/v0/token',
    #   headers=self.auth_headers
    # )
    # self.token = json.loads(response.data)['token']

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
    res_data = json.loads(response.data)
    self.assertEqual(res_data['trip']['name'], data['name'])
    self.assertIn('uri', res_data['trip'].keys())

  def test_get_trip_by_id(self):
    # Create a trip
    trip_name = "My Trip"
    trip_start = date(year=1970, month=1, day=1)
    trip_end = date(year=1970, month=1, day=31)
    test_trip = TripsTest.create_trip(
      name=trip_name,
      start=trip_start,
      end=trip_end
    )

    response = self.client.get(
      '/api/v0/trips/%s' % (test_trip.id,),
      headers=self.auth_headers
    )
    self.assertEqual(response.status_code, 200)
    res_data = json.loads(response.data)
    self.assertEqual(res_data['trip']['name'], trip_name)
