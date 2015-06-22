# -*- coding: utf-8 -*-
import json
from base64 import b64encode

from flask import Flask
from flask.ext.testing import TestCase

from application import db
from api.exceptions import InvalidAPIUsage
from common.tests import BaseTestCase


class ExceptionsTest(BaseTestCase):

  def setUp(self):
    with self.app.app_context():
      db.create_all()

  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

  def test_invalid_api_usage_exception(self):
    try:
      raise InvalidAPIUsage(message="Not Authorized", status_code=403)
    except Exception as exp:
      self.assertEqual(exp.status_code, 403)
      self.assertEqual(exp.message, "Not Authorized")
