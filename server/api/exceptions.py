from flask import jsonify

from common.exceptions import BaseException


class InvalidAPIUsage(BaseException):

  def __init__(self, message, status_code=400, payload=None):
    BaseException.__init__(self, message, status_code, payload)
