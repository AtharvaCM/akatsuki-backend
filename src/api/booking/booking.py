# booking blueprint
# All booking related API will be maintained here

from flask import Blueprint
from flask_restful import Api, Resource

booking = Blueprint('booking', __name__, url_prefix='/api/v1/booking')


class Booking(Resource):
    def get(self):
        return 'Booking'


api = Api(booking)
api.add_resource(Booking, '/')
