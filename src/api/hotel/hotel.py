# Hotel blueprint
# All hotel related API will be maintained here
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

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


class LocationList(Resource):
    def get(self):
        locations = db.session.query(Hotel.city).distinct().all()
        print(locations)
        locations_list = []

        for loc in locations:
            (location,) = loc
            locations_list.append(location)

        return jsonify(dict(data=locations_list))


api.add_resource(LocationList, '/locations', endpoint="location_list")


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

        # subquery = db.session.query(Booking.hotel_id
        #                             ).filter(Booking.check_in_date >= check_in_date
        #                                      ).filter(Booking.check_out_date <= check_out_date).subquery()

        # subquery1 = db.session.query(Hotel.id
        #                              ).filter(Hotel.city == location
        #                                       ).subquery()

        # get all the hotels that are booked for the given date range
        # hotel_id_list = db.session.query(Hotel
        #                                  ).filter(Booking.hotel_id.not_in(subquery1)
        #                                           ).filter(Booking.check_in_date >= check_in_date
        #                                                    ).filter(Booking.check_out_date <= check_out_date).distinct().all()

        # print('hotel_id_list', hotel_id_list)

        # available_hotels = []
        # get all the rooms for the given hotel_id for the given date range
        # for hotel_id in [5]:
        #     rooms = db.session.query(Booking.room_id).filter(
        #         Booking.hotel_id == hotel_id).distinct().all()
        #     print("rooms", rooms)
        #     for room in rooms:
        #         # get sum of booked rooms for room type
        #         room_count_tuple = db.session.query(db.func.sum(
        #             Booking.number_of_rooms)).filter(Booking.room_id == 14).first()
        #         (room_count,) = room_count_tuple
        #         print("room_count", room_count)
        #         if room_count > 0:
        #             available_hotels.append(hotel_id)

        # print(available_hotels)

        # subquery2 = db.session.query(Room
        # ).filter(Room.available_rooms>0
        # ).filter(Hotel.id.not_in(subquery1)).subquery()

        # get all hotels for the given location
        # pagination = db.session.query(Hotel
        #                               ).filter(Hotel.city == location
        #                                        ).filter(Hotel.id.not_in(subquery)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

        pagination = db.session.query(Hotel
                                      ).filter(Hotel.city == location
                                               ).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

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
