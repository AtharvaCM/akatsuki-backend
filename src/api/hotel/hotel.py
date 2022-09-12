# Hotel blueprint
# All hotel related API will be maintained here

import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, marshal_with, fields
from src.database import db

# importing Model
from src.models import Hotel, Booking, Room
from sqlalchemy.sql import func

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# default values
DEFAULT_LOCATION = 'Manali'
DEFAULT_CHECK_IN_DATE = '9/13/2022'#getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = '9/14/2022'#getNextDate("%m/%d/%y")
DEFAULT_PAGE = 1

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()


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

        query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum_b')
        #).filter(Booking.room_id == Room.id
        ).filter(Booking.check_in_date >= check_in_date
        ).filter(Booking.check_out_date <= check_out_date
        ).group_by(Booking.room_id).subquery()

        subquery2 = db.session.query(Room.id
        ).filter(Room.id == (query.c.room_id)     
        ).filter(Room.total_rooms <= (query.c.sum_b)).subquery()

        subquery3 = db.session.query(Room.hotel_id
        ).filter(Room.id.not_in(subquery2)
        ).filter(Room.total_rooms > 0).subquery()

        pagination = db.session.query(Hotel
        ).filter(Hotel.city == location            
        ).filter(Hotel.id.in_(subquery3)).order_by(Hotel.ratings.desc()).all()

        return pagination
        

api.add_resource(HotelList, '/')
