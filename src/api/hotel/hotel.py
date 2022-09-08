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

        subquery = db.session.query(Booking.hotel_id
                                    ).filter(Booking.check_in_date >= check_in_date
                                             ).filter(Booking.check_out_date <= check_out_date).subquery()

        pagination = db.session.query(Hotel
                                      ).filter(Hotel.city == location
                                               ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

        show = requested_columns(request)
        response = []

        for hotel in pagination.items:
            response.append(hotel.to_dict(show=show))

        return jsonify(dict(has_next=pagination.has_next, data=response))


api.add_resource(HotelList, '/', endpoint="hotel_list")


class HotelDetails(Resource):
    def get(self, id):
        hotel = Hotel.query.filter_by(id=id).first()

        return jsonify(dict(data=hotel))


api.add_resource(HotelDetails, '/<int:id>')


class RoomList(Resource):
    def get(self, id):
        rooms = db.session.query(
            Room.room_type).filter_by(hotel_id=id)

        return jsonify(dict(data=rooms))


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
