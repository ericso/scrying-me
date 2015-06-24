# -*- coding: utf-8 -*-
import calendar, datetime


def convert_date_to_datetime(obj):
  return datetime.datetime.combine(obj, datetime.datetime.min.time())

def date_to_mills_json_serializer(obj):
  """Default JSON serializer
  """
  # convert date object to epoch time in milliseconds
  obj = convert_date_to_datetime(obj)
  if isinstance(obj, datetime.datetime):
    if obj.utcoffset() is not None:
      obj = obj - obj.utcoffset()
  millis = int(
    calendar.timegm(obj.timetuple()) * 1000 +
    obj.microsecond / 1000
  )
  return millis

def date_serializer(obj):
  return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def user_json_serializer(obj):
  """Converts a User object into a dict for API response
  """
  return dict(username=obj.username)
