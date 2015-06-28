# -*- coding: utf-8 -*-
import json
from datetime import datetime
from datetime import time

from flask import Blueprint, current_app
from flask import jsonify, url_for
from flask import g, abort, request, Response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse, fields, marshal

from application import db, api
from app.models import Trip
from app.users import auth
from common.http import add_cors_headers


trips_blueprint = Blueprint('trips_blueprint', __name__)

@trips_blueprint.after_request
def after_request(response):
  return add_cors_headers(response)

trip_fields = {
  'name': fields.String,
  'start': fields.DateTime(dt_format='iso8601'),
  'end': fields.DateTime(dt_format='iso8601'),
  'uri': fields.Url('trip')
}

class TripListAPI(Resource):

  decorators = [auth.login_required]

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('name',
                               type=str,
                               required=True,
                               help="No trip name provided",
                               location='json')
    self.reqparse.add_argument('start',
                               required=True,
                               help="No trip start date provided",
                               location='json')
    self.reqparse.add_argument('end',
                               required=True,
                               help="No trip end date provided",
                               location='json')
    super(TripListAPI, self).__init__()

  def get(self):
    trips = Trip.query.all()
    rv = list()
    for trip in trips:
      rv.append(marshal(trip, trip_fields))
    return {'data': rv}, 200

  def post(self):
    if request.headers['content-type'] == 'application/json':
      args = self.reqparse.parse_args()
      name = args['name']
      start = args['start']
      end = args['end']

      trip = Trip(name=name, start=start, end=end)
      db.session.add(trip)
      db.session.commit()
      return {'trip': marshal(trip, trip_fields)}, 201
    else:
      return Response(status=405) # invalid request type


class TripAPI(Resource):

  decorators = [auth.login_required]

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('name',
                               type=str,
                               required=True,
                               help="No trip name provided",
                               location='json')
    self.reqparse.add_argument('start',
                               required=True,
                               help="No trip start date provided",
                               location='json')
    self.reqparse.add_argument('end',
                               required=True,
                               help="No trip end date provided",
                               location='json')
    super(TripAPI, self).__init__()

  def get(self, id):
    if id is None:
      abort(400) # missing arguments
    trip = Trip.query.get(id)
    if trip is None:
      abort(400) # no trip found
    return {'trip': marshal(trip, trip_fields)}, 200

  def put(self, id):
    pass

  def delete(self, id):
    pass
