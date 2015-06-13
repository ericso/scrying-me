import unittest

from flask import Flask
from flask.ext.testing import TestCase

class ApiTest(TestCase):

  def create_app(self):
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

  def test_create_user(self):
    response = self.client.post('/api/users')
    self.assert_404(response)


if __name__ == '__main__':
  unittest.main()
