# Hotel blueprint
# All hotel related API will be maintained here
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort, marshal_with, fields

from flasgger import swag_from

from src.database import db

# importing Model
from src.models import Hotel, Booking, requested_columns, Room

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


class HotelList(Resource):
    @swag_from('./docs/hotel/hotel_list.yaml', endpoint="hotel.hotel_list")
    def get(self):
        # getting query params
        location = request.args.get('location', DEFAULT_LOCATION, type=str)
        check_in_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_IN_DATE, type=str)
        check_out_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_OUT_DATE, type=str)
        page = request.args.get('page', DEFAULT_PAGE, type=int)

        show = requested_columns(request)

        subquery = db.session.query(Booking.hotel_id
                                    ).filter(Booking.check_in_date >= check_in_date
                                             ).filter(Booking.check_out_date <= check_out_date).subquery()

        subquery1 = db.session.query(Booking.hotel_id
                                     ).filter(Booking.check_in_date >= check_in_date
                                              ).filter(Booking.check_out_date <= check_out_date).subquery()

        subquery2 = db.session.query(Hotel
                                     ).filter(Hotel.city == location
                                              ).filter(Hotel.id.in_(subquery1)).distinct().all()

        # get all the hotels that are booked for the given date range
        hotel_id_list = db.session.query(Booking.hotel_id
                                         ).filter(db.and_(Hotel.id == Booking.hotel_id, Hotel.city == location)
                                                  ).filter(Booking.check_in_date >= check_in_date
                                                           ).filter(Booking.check_out_date <= check_out_date).distinct().all()

        print('hotel_id_list', hotel_id_list)

        room_types_available = []
        # get all the rooms for the given hotel_id for the given date range
        for hotel_id in [5]:
            rooms = db.session.query(Booking.room_id).filter(
                Booking.hotel_id == hotel_id).distinct().all()
            print("rooms", rooms)
        for room in rooms:
            # get sum of booked rooms for room type
            room_count = db.session.query(db.func.sum(
                Booking.number_of_rooms)).filter(Booking.room_id == 14).all()
            print("room_count", room_count)

        # print(room_types_available)

        # subquery2 = db.session.query(Room
        # ).filter(Room.available_rooms>0
        # ).filter(Hotel.id.not_in(subquery1)).subquery()

        # get all hotels for the given location
        pagination = db.session.query(Hotel
                                      ).filter(Hotel.city == location
                                               ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

        hotels_serialized = []

        for hotel in pagination.items:
            hotels_serialized.append(hotel.to_dict(show=show))

        return jsonify(dict(has_next=pagination.has_next, data=hotels_serialized))


api.add_resource(HotelList, '/', endpoint="hotel_list")


class HotelDetails(Resource):
    def get(self, id):
        hotel = Hotel.query.filter_by(id=id).first()

        show = requested_columns(request)
        hotel_serialized = hotel.to_dict(show=show)

        return jsonify(dict(data=hotel_serialized))


api.add_resource(HotelDetails, '/<int:id>')


class RoomList(Resource):
    def get(self, id):
        rooms = db.session.query(Room).filter(Room.hotel_id == id).all()

        show = requested_columns(request)
        rooms_serialized = []

        for room in rooms:
            rooms_serialized.append(room.to_dict(show=show))

        return jsonify(dict(data=rooms_serialized))


api.add_resource(RoomList, '/<int:id>/rooms')

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
