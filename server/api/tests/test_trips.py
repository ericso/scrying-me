# -*- coding: utf-8 -*-
import json
from base64 import b64encode
from datetime import date

from flask import Flask
from flask.ext.testing import TestCase

from application import db
from api.models import Trip
from api.serializers import date_serializer
from api.tests.test_users import UsersTest
from common.tests import BaseTestCase
from common.util import rand_string_gen, rand_date


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

  @staticmethod
  def generate_test_trips(n=1):
    """Returns a list of n test trips
    """
    rv = list()
    # seed dates
    seed_start = date(year=1970, month=1, day=1)
    seed_end = date(year=1971, month=1, day=1)
    for i in xrange(0, n):
      start, end = rand_date(seed_start, seed_end)
      rv.append({
        'name': rand_string_gen(),
        'start': start,
        'end': end
      })
    return rv

  ### Tests ###
  def test_get_all_trips(self):
    # create a user to own the trips
    test_username = 'test_username'
    test_password = 'test_password'
    test_user = UsersTest.create_user(test_username, test_password)
    auth_headers = UsersTest.create_basic_auth_header(
      username=test_username,
      password=test_password
    )

    # create the trips
    num_trips = 5
    trips = TripsTest.generate_test_trips(num_trips)
    for trip in trips:
      # TODO(eso) modify to take a user as an owner
      TripsTest.create_trip(trip['name'], trip['start'], trip['end'])

    response = self.client.get(
      '/api/v0/trips',
      headers=auth_headers
    )
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    trips = data['data']
    self.assertEqual(len(trips), num_trips)

  # TODO(eso) write these tests
  # def test_get_trip_by_id(self):
  #   self.fail("finish test")

  # def test_get_trip_not_found(self):
  #   response = self.client.get(
  #     '/api/v0/trips/999', # this trip doesn't exist
  #     headers=self.auth_headers
  #   )
  #   self.assertEqual(response.status_code, 404)

  # def test_create_new_trip_but_missing_arguments(self):
  #   response = self.client.post(
  #     '/api/v0/trips',
  #     content_type='application/json'
  #   )
  #   self.assertEqual(response.status_code, 400)

  # def test_create_new_trip_but_invalid_request_type(self):
  #   response = self.client.post(
  #     '/api/v0/trips',
  #     content_type='text/html'
  #   )
  #   self.assertEqual(response.status_code, 400)

  def test_create_new_trip_successfully(self):
    headers = dict()
    headers.update({'Content-Type': 'application/json'})

    # have the trip start on Jan 1, 1970 and end on Jan 31, 1970
    date_start = date(year=1970, month=1, day=1)
    date_end = date(year=1970, month=1, day=31)
    data = dict(name='test_trip', start=date_start, end=date_end)
    json_data = json.dumps(data, default=date_serializer)
    json_data_length = len(json_data)
    headers['Content-Length'] =  json_data_length

    # add authorization headers
    headers.update(self.auth_headers)

    response = self.client.post(
      '/api/v0/trips',
      headers=headers,
      data=json_data
    )
    self.assertEqual(response.status_code, 201)
    res_data = json.loads(response.data)
    print(res_data)
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
