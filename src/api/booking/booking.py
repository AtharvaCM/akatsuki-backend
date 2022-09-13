# booking blueprint
# All booking related API will be maintained here

import json
from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from datetime import date
from src.services.dateHepler import getCurrentDate, getNextDate
from flask_restful import Resource, Api, reqparse
from src.database import db
from flask import request
from src.models import Hotel, Booking, requested_columns

Booking = Blueprint('Booking', __name__, url_prefix='/api/v1/booking')


class Booking(Resource):
    def get(self):
        return 'Booking'
    
'''
DEFAULT_BOOKING_CODE = 102
DEFAULT_USER_ID = 11
DEFAULT_BOOKING_DATE = 21/2/2020
DEFAULT_TOTAL_AMOUNT = 20000
DEFAULT_PAYMENT_METHOD = "CREDIT_CARD"
DEFAULT_DATES = 15/3/2020 - 20/3/2020
DEFAULT_TRAVELERS = 2
DEFAULT_NO_OF_ROOMS = 1
DEFAULT_CHECK_IN_DATE = getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = getNextDate("%m/%d/%y")
DEFAULT_ROOM_TYPE = "deluxe"
'''

hotel_post_args = reqparse.RequestParser()

'''
hotel_post_args.add_argument('booking_code', type=int, required=True)
hotel_post_args.add_argument('booking_date', type=date, required=True)
hotel_post_args.add_argument('total_amount', type=int, required=True)
hotel_post_args.add_argument('payment_method', type=str, required=True)
hotel_post_args.add_argument('dates', type=date, required=True)
hotel_post_args.add_argument('travelers', type=int, required=True)
hotel_post_args.add_argument('no_of_rooms', type=str)
hotel_post_args.add_argument('user_id', type=int, required=True)
hotel_post_args.add_argument('check_in_date', type=date, required=True)
hotel_post_args.add_argument('check_out_date', type=date, required=True)
hotel_post_args.add_argument('room_type', type=str, required=True)
'''
'''
{
"user_id" : 11,
"booking_code": 101,
"booking_date" : "21/2/2020",
"total_amount" : 20000,
"payment_method" : "CREDIT_CARD",
"travelers" : 2,
"no_of_rooms" : 1,
"check_in_date" : "15/3/2020",
"check_out_date" : "21/3/2020",
"room_type" : "deluxe"
}'''

class BookingConfirm(Resource):
    def post(self):
        new_Booking = Booking(user_id = request.json.get('user_id', type=int), 
                              booking_code =  request.json.get('booking_code', type= int),
                              booking_date =  request.json.get('booking_date', type=date),
                              total_amount =  request.json.get('total_amount', type=int),
                              payment_method = request.json.get('payment_method', type=str),
                              travelers = request.json.get('travelers', type= int),
                              no_of_rooms = request.json.get('no_of_rooms', type= int),
                              check_in_date = request.json.get('check_in_date', type=date),
                              check_out_date = request.json.get('check_out_date', type=date),
                              room_type = request.json.get('room_type', type=str))
        db.session.add(new_Booking)
        db.session.commit()
        show = requested_columns(request)
        Booking_serialized = new_Booking.to_dict(show=show)
        return jsonify(dict(data=Booking_serialized))
    
api = Api(Booking)
api.add_resource(BookingConfirm , '/')
