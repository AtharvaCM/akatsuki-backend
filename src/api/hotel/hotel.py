# Hotel blueprint
# All hotel related API will be maintained here
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

from flasgger import swag_from
from sqlalchemy.sql import func

from src.database import db

# importing Model
from src.models import Hotel, Booking, requested_columns, Room

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# default values
DEFAULT_LOCATION = 'Kovalam'
DEFAULT_CHECK_IN_DATE = '2022-09-13'  # getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = '2022-09-14'  # getNextDate("%m/%d/%y")
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
    # @swag_from('./docs/hotel/hotel_list.yaml', endpoint="hotel.hotel_list")
    def get(self):
        # getting query params
        location = request.args.get('location', DEFAULT_LOCATION, type=str)
        check_in_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_IN_DATE, type=str)
        check_out_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_OUT_DATE, type=str)
        page = request.args.get('page', DEFAULT_PAGE, type=int)

        show = requested_columns(request)

        query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum_b')
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
                                               ).filter(Hotel.id.in_(subquery3)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

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
        check_in_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_IN_DATE, type=str)
        check_out_date = request.args.get(
            'check_in_date', DEFAULT_CHECK_OUT_DATE, type=str)

        query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum_b')
                                 ).filter(Booking.check_in_date >= check_in_date
                                          ).filter(Booking.check_out_date <= check_out_date
                                                   ).group_by(Booking.room_id).subquery()

        subquery2 = db.session.query(Room.id
                                     ).filter(Room.id == (query.c.room_id)
                                              ).filter(Room.total_rooms == (query.c.sum_b)).subquery()

        available_rooms = db.session.query(Room
                                           ).filter(Room.id.not_in(subquery2)
                                                    ).filter(Room.total_rooms > 0
                                                             ).filter(Room.hotel_id == id).all()

        # Calculating the total numbers of rooms booked for a particular hotel

        total_rooms_booked = [r[1] for r in db.session.query(Booking.hotel_id, db.func.sum(Booking.number_of_rooms).label('sum_r')
                                                             ).filter(Booking.check_in_date >= check_in_date
                                                                      ).filter(Booking.check_out_date <= check_out_date
                                                                               ).filter(Booking.hotel_id == id).group_by(Booking.hotel_id)]

        print(f'Total number of rooms booked : {total_rooms_booked}')

        # Calculating the total numbers of rooms in a particular hotel
        total_no_rooms = [row[1] for row in db.session.query(Room.hotel_id, db.func.sum(Room.total_rooms).label('sum_t')
                                                             ).filter(Room.hotel_id == id).group_by(Room.hotel_id)]

        print(f'Total number of rooms in hotel : {total_no_rooms}')

        hiked = int(total_no_rooms[0]*0.8)
        print(f'80% of Total num of rooms : {hiked}')
        is_Hiked = False
        if (len(total_rooms_booked) > 0):
            is_Hiked = total_rooms_booked[0] >= hiked

        print(is_Hiked)

        show = requested_columns(request)
        rooms_serialized = []

        for room in available_rooms:
            # Write query here
            no_of_rooms_booked_query = ''
            room_dict = room.to_dict(show=show)
            room_dict['available_rooms'] = room.total_rooms - \
                no_of_rooms_booked_query
            rooms_serialized.append(room_dict)

        return jsonify(dict(data=rooms_serialized, isHiked=is_Hiked))


api.add_resource(RoomList, '/<int:id>/rooms')
