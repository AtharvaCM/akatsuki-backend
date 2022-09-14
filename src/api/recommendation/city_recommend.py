from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

from flasgger import swag_from
from sqlalchemy.sql import func

from src.database import db

# importing Model
from src.models import Usercitysearch, User, requested_columns

# date helper
from src.services.dateHepler import getCurrentDate, getNextDate

# error codes
from src.api.error import errors

# default values
DEFAULT_LOCATION = 'Kovalam'

hotel = Blueprint("hotel", __name__, url_prefix="/api/v1/hotels")
api = Api(hotel)

parser = reqparse.RequestParser()

class CityRecommendList(Resource):
    def get(self, id):
        city = db.session.query(Usercitysearch.city
        ).filter(Usercitysearch.search_count>=3
        ).filter(Usercitysearch.user_id == id).distinct().all()
        print(city)
        city_list = []

        for city in city_list:
            (cities,) = city
            city_list.append(cities)

        return jsonify(dict(data=city_list))

api.add_resource(CityRecommendList, '/<int:id>/citysearch')