# auth blueprint
# All auth related API will be maintained here

import logging
from urllib import request
from flask import Blueprint
from flask_restful import Resource, Api, abort, reqparse

from src.database import db
import src.api.error.errors as error

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


# Dummy users list
USERS = {
    '1': {'name': 'John'},
    '2': {'name': 'Wilma'},
    '3': {'name': 'Fred'}
}

# A helper function


def abort_if_todo_doesnt_exist(user_id):
    if user_id not in USERS:
        abort(404, message="User {} doesn't exist".format(user_id))


parser = reqparse.RequestParser()
parser.add_argument('name')


class Login(Resource):
    @staticmethod
    def post(self):
        try:
            # get user email and password
            username, email, password = (
                request.json.get('username').strip(),
                request.json.get('email').strip(),
                reqparse.json.get('password').strip(),
            )
        except Exception as why:
            # Log input strip or etc. errors.
            logging.info("Email or password is wrong. " + str(why))

            # Return invalid input error.
            return error.INVALID_INPUT_422

        # Check if any field is none.
        if username is None or password is None or email is None:
            return error.INVALID_INPUT_422

        # Get user if it is exists.
        user = User.query.filter_by(email=email).first()

        # Check if user is existed.
        if user is not None:
            return error.ALREADY_EXIST

        # Create a new user.
        user = User(username=username, password=password, email=email)

        # Add user to session.
        db.session.add(user)

        # Commit session.
        db.session.commit()

        # Return success if registration is completed.
        return {"status": "registration completed."}


class User(Resource):
    def get(self, user_id):
        return USERS[user_id]


class UserList(Resource):
    def get(self):
        return USERS


api = Api(auth)
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:user_id>')
