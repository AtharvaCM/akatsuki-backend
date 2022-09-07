# Hotel blueprint
# All hotel related API will be maintained here

import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, marshal_with, fields
from src.database import db

# importing Model
from src.models import Hotel, Booking
# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# default values
DEFAULT_LOCATION = 'Kovalam'
DEFAULT_CHECK_IN_DATE = getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = getNextDate("%m/%d/%y")
DEFAULT_PAGE = 1

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

hotel_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "address": fields.String,
    "description": fields.String,
    "ratings": fields.Integer,
    "tags": fields.List(fields.String),
    "city": fields.String,
    "state": fields.String,
    "country": fields.String,
    "features": fields.List(fields.String),
    "room_images": fields.List(fields.String),
    "hotel_dp": fields.String,
    #"has_next": fields.Integer
}

# Get the list of hotels available for check_in_date and check_out_date at provided location


class HotelList(Resource):
    @marshal_with(hotel_fields)
    def get(self):
        # getting query params
        location = request.args.get('location', DEFAULT_LOCATION, type=str)
        check_in_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_IN_DATE, type=str)
        check_out_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_OUT_DATE, type=str)
        page = request.args.get('page', DEFAULT_PAGE, type=int)
        

        subquery = db.session.query(Booking.hotel_id
        ).filter(Booking.check_in_date >= check_in_date
        ).filter(Booking.check_out_date <= check_out_date).subquery()

        '''
        hotels = db.session.query(Hotel
        ).filter(Hotel.city == location            
        ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).all()
        
        '''
        
        pagination = db.session.query(Hotel
        ).filter(Hotel.city == location            
        ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)


        return pagination.items
        

api.add_resource(HotelList, '/')
