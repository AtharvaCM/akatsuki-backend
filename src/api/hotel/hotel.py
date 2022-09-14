# Hotel blueprint
# All hotel related API will be maintained here
from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

# from flasgger.utils import swag_from, Swagger
from flasgger.utils import swag_from
from src.database import db

# importing Model
from src.models import Hotel, Booking, Model, Review, Room, requested_columns

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# error codes
from src.api.error import errors

# default values
DEFAULT_LOCATION = 'Goa'
DEFAULT_CHECK_IN_DATE ='2022-9-22' #getCurrentDate("%m/%d/%y")
DEFAULT_CHECK_OUT_DATE ='2022-9-25' #getCurrentDategetNextDate("%m/%d/%y")
DEFAULT_PAGE = 1

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()


# GET - returns a list of all distinct locations from the Hotel table
class LocationList(Resource):
    @swag_from('/src/docs/hotel/location_list.yml', endpoint="hotel.location_list")
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
    @swag_from('/src/docs/hotel/hotel_list.yml', endpoint="hotel.hotel_list")
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


# GET - returns details of a particular hotel
class HotelDetails(Resource):
    @swag_from('/src/docs/hotel/hotel_details.yml')
    def get(self, id):
    
        hotel = Hotel.query.filter_by(id=id).first()

        show = requested_columns(request)
        hotel_serialized = hotel.to_dict(show=show)

        return jsonify(dict(data=hotel_serialized))


api.add_resource(HotelDetails, '/<int:id>')

# GET - returns Roomlist of a particular hotel
class RoomList(Resource):
    @swag_from('/src/docs/hotel/room_list.yml')
    def get(self, id):
        rooms = db.session.query(Room).filter(Room.hotel_id == id).all()

        show = requested_columns(request)
        rooms_serialized = []

        for room in rooms:
            rooms_serialized.append(room.to_dict(show=show))

        return jsonify(dict(data=rooms_serialized))


api.add_resource(RoomList, '/<int:id>/rooms')

# GET - returns a list of extra features for a given hotel


class ExtrafeaturesList(Resource):
    @swag_from('/src/docs/hotel/extra_feature.yml')
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
    @swag_from('/src/docs/hotel/review_list_get.yml')
    def get(self, id):
        # the hotel for which we want to get all reviews
        hotel = Hotel.query.filter_by(id=id).first()
        reviews = hotel.reviews

        show = requested_columns(request)
        reviews_serialized = []

        for review in reviews:
            reviews_serialized.append(review.to_dict(show=show))

        return jsonify(dict(data=reviews_serialized))
    @swag_from('/src/docs/hotel/review_list_post.yml')
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
    @swag_from('/src/docs/hotel/review_details.yml')
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
            return jsonify(dict(message="Review exists", reviewPresent=True))
        else:
            return jsonify(dict(message="Review not found", reviewPresent=False))


api.add_resource(ReviewDetails, '/<int:id>/reviews/check-review')


