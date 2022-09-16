# Hotel blueprint
# All hotel related API will be maintained here
from datetime import datetime
import json
from operator import or_
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

from flasgger import swag_from
from sqlalchemy.sql import func

from src.database import db

# importing Model
from src.models import Hotel, Booking, Model, Review, Room, requested_columns

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# error codes
from src.api.error import errors

# default values
DEFAULT_LOCATION = 'Goa'
DEFAULT_CHECK_IN_DATE = '2022-09-23'#getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE = '2022-09-24'#getNextDate("%m/%d/%y")
DEFAULT_PAGE = 1

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()


# GET - returns a list of all distinct locations from the Hotel table
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

# GET - returns a list of hotels based on location, check-in & check-out date


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

        # This query will return the Sum of rooms booked as per Room ID
        query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum_b')
                                 ).filter(Booking.check_in_date >= check_in_date
                                          ).filter(Booking.check_out_date <= check_out_date
                                                   ).group_by(Booking.room_id).subquery()

        # Query will return the list of Room ID which is fully booked
        subquery2 = db.session.query(Room.id
                                     ).filter(Room.id == (query.c.room_id)
                                              ).filter(Room.total_rooms <= (query.c.sum_b)).subquery()

        # Query will return list of Hotels which is available
        subquery3 = db.session.query(Room.hotel_id
                                     ).filter(Room.id.not_in(subquery2)
                                              ).filter(Room.total_rooms > 0).subquery()

        # Query will return Hotels based on particular location
        pagination = db.session.query(Hotel
                                      ).filter(Hotel.city == location
                                               ).filter(Hotel.id.in_(subquery3)).order_by(Hotel.ratings.desc()).paginate(page, per_page=2)

        hotels_serialized = []

        for hotel in pagination.items:
            hotels_serialized.append(hotel.to_dict(show=show))

        return jsonify(dict(has_next=pagination.has_next, data=hotels_serialized))


api.add_resource(HotelList, '/', endpoint="hotel_list")


# GET - returns details of a particular hotel
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
        
        bookingDateCondition = db.and_(Booking.check_in_date >= check_in_date, Booking.check_out_date <= check_out_date)
        bookingDateCondition2 = db.and_(Booking.check_in_date <= check_in_date, Booking.check_out_date >= check_out_date)

        # Calculating the sum of room booked for a particular room type of a hotel w.r.t check-in and check-out date
        query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum_b')
                                 ).filter(db.or_(bookingDateCondition, bookingDateCondition2)
                                 ).filter(db.or_((Booking.check_in_date == check_in_date),(Booking.check_out_date >= check_out_date))).group_by(Booking.room_id).subquery()
   
        # Getting the list of Room ids which are fully booked
        subquery2 = db.session.query(Room.id
                                     ).filter(db.and_(Room.id == (query.c.room_id),Room.total_rooms == (query.c.sum_b))).subquery()
        
        # Getting the list of Rooms which are available for the selected hotel
        available_rooms = db.session.query(Room
                                            ).filter(Room.id.not_in(subquery2)
	                                                ).filter(Room.hotel_id == id).all()

        isFullyBooked = False
        
        # Calculating the total numbers of rooms booked for a particular hotel w.r.t check-in and check-out date
        '''
        total_rooms_booked = [r for r in db.session.query(Booking.hotel_id, db.func.sum(Booking.number_of_rooms).label('sum_r')
                                                            ).filter(Booking.hotel_id == id
                                                            ).filter(db.or_(bookingDateCondition, bookingDateCondition2)).group_by(Booking.hotel_id)]
        '''
        total_rooms_booked  = [r for r in db.session.query(Booking.hotel_id, db.func.sum(Booking.number_of_rooms).label('sum_r')
                                                              ).filter(Booking.hotel_id == id
                                                              ).filter(Booking.check_in_date>=check_in_date
                                                              ).filter(Booking.check_out_date<=check_out_date).group_by(Booking.hotel_id)]
        
        print(total_rooms_booked)
        # Calculating the total numbers of rooms in a particular hotel
        total_no_rooms = [row[1] for row in db.session.query(Room.hotel_id, db.func.sum(Room.total_rooms).label('sum_t')
                                                             ).filter(Room.hotel_id == id).group_by(Room.hotel_id)]

        print(total_no_rooms)

        hiked = int(total_no_rooms[0]*0.8) #Calculating 80% of total no of rooms
    
        is_Hiked = False
        #Checking if more than *80% rooms are booked or not
        if (len(total_rooms_booked) > 0):
            is_Hiked = total_rooms_booked[0] >= hiked
            isFullyBooked = total_no_rooms[0] == total_rooms_booked.sum_r


        show = requested_columns(request)
        rooms_serialized = []

        # Getting the Sum of Rooms booked for that Room ID
        no_of_rooms_booked_query = db.session.query(Booking.room_id, db.func.sum(Booking.number_of_rooms).label('sum')
                                                        ).filter(db.or_(bookingDateCondition, bookingDateCondition2)
                                                                          ).group_by(Booking.room_id).all()

        # This will return the list of rooms with available rooms attribute
        for room in available_rooms:
            print(room)
            room_dict = room.to_dict(show=show)
            room_dict['available_rooms'] = room.total_rooms
            for bookedRoom in no_of_rooms_booked_query:
                if(room.id == bookedRoom.room_id):
                    room_dict['available_rooms'] = room.total_rooms - bookedRoom.sum
    
            rooms_serialized.append(room_dict)
            
        return jsonify(dict(data=rooms_serialized, isHiked=is_Hiked, isfullybooked=isFullyBooked))


api.add_resource(RoomList, '/<int:id>/rooms')

# GET - returns a list of extra features for a given hotel


class ExtrafeaturesList(Resource):
    def get(self, id):
        # the hotel for which we want to get the extra features
        hotel = Hotel.query.filter_by(id=id).first()
        extra_features = hotel.extra_features

        show = requested_columns(request)
        extrafeatures_serialized = []

        for extra_feature in extra_features:
            extrafeatures_serialized.append(extra_feature.to_dict(show=show))

        return jsonify(dict(data=extrafeatures_serialized))


api.add_resource(ExtrafeaturesList,  '/<int:id>/extrafeatures')


# GET - returns list of reviews for a given hotel
# POST - adds a review if it does not already exist
class ReviewList(Resource):
    def get(self, id):
        # the hotel for which we want to get all reviews
        hotel = Hotel.query.filter_by(id=id).first()
        reviews = hotel.reviews

        show = requested_columns(request)
        reviews_serialized = []

        for review in reviews:
            reviews_serialized.append(review.to_dict(show=show))

        return jsonify(dict(data=reviews_serialized))

    def post(self, id):
        # write the timestamp
        review_date = datetime.now()

        try:
            # Get rating, comment and user_id.
            rating, comment, user_id = (
                request.json.get("rating"),
                request.json.get("comment").strip(),
                request.json.get("user_id"),
            )
        except Exception as why:
            # Log input strip or etc. errors.
            print("user_id, rating or comment is wrong. " + str(why))
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # Check if any field is none.
        if user_id is None or rating is None or comment is None:
            return errors.INVALID_INPUT_422

        # check if review already exists
        review = db.session.query(Review).filter(
            Review.user_id == user_id).filter(Review.hotel_id == id).first()

        if review is not None:
            return errors.ALREADY_EXIST

        # Create new review
        review = Review(review_date=review_date, rating=rating,
                        comment=comment, hotel_id=id, user_id=user_id)

        db.session.add(review)
        db.session.commit()

        return jsonify(dict(status="Review added successfully"))


api.add_resource(ReviewList, '/<int:id>/reviews')


class ReviewDetails(Resource):
    def get(self, id):
        try:
            # Get user_id.
            user_id = request.json.get("user_id")
        except Exception as why:
            # Log input strip or etc. errors.
            print("user_id is wrong. " + str(why))
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # check if review already exists
        review = db.session.query(Review).filter(
            Review.user_id == user_id).filter(Review.hotel_id == id).first()

        if review is not None:
            show = requested_columns(request)
            review_serialized = review.to_dict(show=show)

            return jsonify(dict(data=review_serialized, message="Review exists", reviewPresent=True))
        else:
            return jsonify(dict(data={}, message="Review not found", reviewPresent=False))


api.add_resource(ReviewDetails, '/<int:id>/reviews/check-review')
