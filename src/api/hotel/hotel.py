# Hotel blueprint
# All hotel related API will be maintained here

import json
from urllib import request
from flask import Blueprint
from flask import jsonify
from flask_restful import Resource, Api, reqparse, abort

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()

# importing Model
# from src.models.HotelModel.py import Hotel

class HotelList(Resource):
    def get(self):
        location=parser.add_argument('location', type=str, location='args')
        check_in_date=parser.add_argument('check_in_date', type=str, location='args')
        check_out_date=parser.add_argument('check_out_date', type=str, location='args')
        return jsonify(parser.parse_args(location, check_in_date, check_out_date))
    
api.add_resource(HotelList, '/')

