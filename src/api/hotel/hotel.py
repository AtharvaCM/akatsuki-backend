# Hotel blueprint
# All hotel related API will be maintained here

import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort

# importing Model
from src.models import Hotel

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# default values
DEFAULT_LOCATION = 'Fallback_Pune'
DEFAULT_CHECK_IN_DATE = getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = getNextDate("%m/%d/%y")

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()

# class HotelList(Resource):
#     def get(self):
#         parser.add_argument('location', type=str, location='args')
#         parser.add_argument(
#             'check_in_date', type=str, location='args')
#         parser.add_argument(
#             'check_out_date', type=str, location='args')

#         return jsonify(parser.parse_args(location, check_in_date, check_out_date))


class HotelList(Resource):
    def get(self):
        # getting query params
        location = request.args.get('location', DEFAULT_LOCATION, type=str)
        check_in_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_IN_DATE, type=str)
        check_out_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_OUT_DATE, type=str)

        hotels = Hotel.query.all()      # we can add limit using limit() method
        jsonHotels = json.dumps(hotels)
        print(jsonHotels)

        return jsonify(dict(hotels=hotels))


api.add_resource(HotelList, '/')
      