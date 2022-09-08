# Hotel blueprint
# All hotel related API will be maintained here

from cgitb import text
from datetime import date
import json
from os import O_RANDOM
from tkinter.tix import COLUMN
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, marshal_with, fields
from src.database import db

# importing Model
from src.models import Hotel, Booking, Room
# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# default values
DEFAULT_LOCATION = 'Kovalam'
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
    "room_type":fields.String

}

hotel_room_type = {
    "room_type": fields.List(fields.String)
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

        print(location)

        subquery = db.session.query(Booking.hotel_id
        ).filter(Booking.check_in_date >= check_in_date
        ).filter(Booking.check_out_date <= check_out_date).subquery()

        hotels = db.session.query(Hotel
        ).filter(Hotel.city == location            
        ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).all()
        #hotels = db.session.query(Hotel, Booking).filter(db.and_(Hotel.city == 'Kovalam', Hotel.id.not_in(Booking.hotel_id))).all()
        
        return hotels

api.add_resource(HotelList, '/')

class HotelDetails(Resource):
    @marshal_with(hotel_fields)
    def get(self,id):
        #hotel_id = parser.add_argument('id', type=int)
        hotel = Hotel.query.filter_by(id = id).first()  
        
        return hotel
    
api.add_resource(HotelDetails, '/<int:id>')

class RoomType(Resource):
    @marshal_with(hotel_room_type)
    def get(self, id):
        Room_type = db.session.query(Hotel.room_type).filter_by(id = id).first()
        
        return Room_type

api.add_resource(RoomType, '/<int:id>/Room_type')

'''
hotel_post_args = reqparse.RequestParser()
hotel_post_args.add_argument('booking_code', type=int, required=True)
hotel_post_args.add_argument('booking_date', type=date, required=True)
hotel_post_args.add_argument('total_amount', type=int, required=True)
hotel_post_args.add_argument('payment_method', type=str, required=True)
hotel_post_args.add_argument('dates', type=date, required=True)
hotel_post_args.add_argument('travelers', type=int, required=True)
hotel_post_args.add_argument('no_of_rooms', type=str, required=True)

class BookingConfirm(Resource):
    def post(self, HotelDetails):
	    temp = {'Hotels': name}
		.append(temp)
		return temp
'''