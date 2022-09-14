# booking blueprint
# All booking related API will be maintained here

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

from datetime import datetime

from src.database import db
from src.api.error import errors
from src.models import Booking


booking = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')
api = Api(booking)


class Bookings(Resource):
    def post(self):
        # Write the timestamp
        booking_date = datetime.now()

        # get params from request body
        try:
            user_id, room_type, check_in_date, check_out_date, amount, number_of_rooms, hotel_id, room_id = (
                request.json.get('user_id'),
                request.json.get('room_type').strip(),
                request.json.get('check_in_date').strip(),
                request.json.get('check_out_date').strip(),
                request.json.get('amount'),
                request.json.get('number_of_rooms'),
                request.json.get('hotel_id'),
                request.json.get('room_id'),
            )
        except Exception as why:
            # Log input strip or etc. errors.
            print("input is wrong. " + str(why))
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # check if any field is None
        if user_id is None or room_type is None or check_in_date is None or check_out_date is None or amount is None or number_of_rooms is None or hotel_id is None or room_id is None:
            return errors.INVALID_INPUT_422

        # generate a booking code
        rand_int = datetime.now().time()
        print(rand_int)
        booking_code = 'bcode1'

        # static fields
        payment = 'Credit Card'
        travelers = 1

        # create a new booking
        try:
            new_Booking = Booking(booking_code=booking_code, room_type=room_type,
                                  check_in_date=check_in_date, check_out_date=check_out_date,
                                  amount=amount, payment=payment, number_of_rooms=number_of_rooms,
                                  booking_date=booking_date, travelers=travelers, user_id=user_id,
                                  hotel_id=hotel_id, room_id=room_id)
        except Exception as why:
            # Log input strip or etc. errors.
            print("something is wrong. " + str(why))
            return errors.SERVER_ERROR_500

        db.session.add(new_Booking)
        db.session.commit()

        return jsonify(dict(status="Booking successful"))


api.add_resource(Bookings, '/')
