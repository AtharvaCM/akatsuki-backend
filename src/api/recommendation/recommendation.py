from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

from flasgger import swag_from

from src.database import db

# importing Model
from src.models import Room, Usercitysearch, User, Userhotelsearch, Hotel, requested_columns

# error codes
from src.api.error import errors

recommendation = Blueprint("recommendation", __name__,
                           url_prefix="/api/v1/recommendation")
api = Api(recommendation)

parser = reqparse.RequestParser()


class CityRecommendList(Resource):
    def get(self):

        id = request.args.get('id', type=int)
        city = db.session.query(Usercitysearch
                                ).filter(Usercitysearch.search_count >= 5
                                         ).filter(Usercitysearch.user_id == id).limit(4).all()

        show = requested_columns(request)
        city_serialized = []

        for loc in city:
            city_serialized.append(loc.to_dict(show=show))

        return jsonify(dict(data=city_serialized))

    def post(self):
        id = request.args.get('id', type=int)
        city = request.args.get('city', type=str)

        # check if city already exists based on search
        citysearch = Usercitysearch.query.filter(db.and_(Usercitysearch.user_id == id,
                                                         Usercitysearch.city == city)).first()

        if citysearch is not None:
            count = citysearch.search_count + 1
            print(count)
            setattr(citysearch, 'search_count', count)
            # db.session.add(cityrecordupdate)
            db.session.commit()
            return jsonify(dict(status="City record updated successfully"))
        else:
            # Create new record for that city
            cityrecord = Usercitysearch(city=city, search_count=1, user_id=id)
            db.session.add(cityrecord)
            db.session.commit()
            return jsonify(dict(status="City record added successfully"))


class HotelRecommendList(Resource):
    def get(self):
        try:
            # get user_id
            id = request.args.get('id', type=int)
        except Exception as why:
            # Log input strip or etc. errors.
            print("user_id is wrong. " + str(why))
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # check if user_id is not None
        if id is None:
            return errors.INVALID_INPUT_422

        # get hotel ids from search table
        subquery = db.session.query(Userhotelsearch.hotel_id
                                    ).filter(Userhotelsearch.search_count >= 5
                                             ).filter(Userhotelsearch.user_id == id).subquery()

        hotels = db.session.query(Hotel).filter(
            Hotel.id.in_(subquery)).limit(4).all()

        # if hotels are not found
        if len(hotels) == 0:
            return jsonify(dict(data=None, hotels_found=False))

        show = requested_columns(request)
        hotel_serialized = []

        for hotel in hotels:
            hotel_dict = {}

            hotel_dict["id"] = hotel.id
            hotel_dict["name"] = hotel.name
            hotel_dict['ratings'] = hotel.ratings
            hotel_dict["hotel_dp"] = hotel.hotel_dp
            # get room prices for this hotel
            (rooms,) = db.session.query(Room.cost).filter(
                Room.hotel_id == hotel.id).order_by(Room.cost).first()
            hotel_dict["price"] = rooms

            hotel_serialized.append(hotel_dict)

        return jsonify(dict(data=hotel_serialized, hotels_found=True))

    def post(self):
        id = request.args.get('id', type=int)
        hotel_id = request.args.get('hotel_id', type=str)

        # check if hotel already exists based on search
        hotelsearch = db.session.query(Userhotelsearch).filter(db.and_(Userhotelsearch.user_id == id,
                                                                       Userhotelsearch.hotel_id == hotel_id)).first()

        if hotelsearch is not None:
            count = hotelsearch.search_count + 1
            print(count)
            setattr(hotelsearch, 'search_count', count)
            db.session.commit()
            return jsonify(dict(status="Hotel record updated successfully"))
        else:
            # Create new record for that hotel
            hotelrecord = Userhotelsearch(
                hotel_id=hotel_id, search_count=1, user_id=id)
            db.session.add(hotelrecord)
            db.session.commit()
            return jsonify(dict(status="Hotel record added successfully"))


api.add_resource(CityRecommendList, '/city')
api.add_resource(HotelRecommendList, '/hotel')
