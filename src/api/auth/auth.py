from flask import jsonify, request, Blueprint, session
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

from src.database import db
from src.models import User
from src.api.error import errors

import jwt
import os

from src.api.error import errors
from src.database import db
from src.models import User

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

SECRET_KEY = os.environ.get("SECRET_KEY")


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing in header'})
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


class Register(Resource):
    def post(self):
        data = request.json
        hashed_password = generate_password_hash(
            data.get('password'), method='sha256')

        new_user = User(id=data.get('id'), name=data.get('name'), username=data.get('username'), email=data.get(
            'email'), password=hashed_password, avatar=data.get('avatar'), created_at=datetime.now(), updated_at=datetime.now())

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'registered successfully'})


class Login(Resource):
    def post(self):
        try:
            id, username, password = (
                request.json.get('id'),
                request.json.get("username"),
                request.json.get("password")
            )
        except Exception as why:
            print("Input is wrong" + str(why))
            return errors.INVALID_INPUT_422

        if username is None or password is None:
            return errors.NO_INPUT_400

        try:
            user = User.query.filter_by(username=username).first()

            if user.password == password:
                session['logged_in'] = True
                token = jwt.encode({id: user.id}, SECRET_KEY, "HS256")

                return jsonify({'token': token, 'is_authenticated': True, 'username': user.username, 'user_id': user.id, 'avatar': user.avatar})

            return jsonify({'Authentication': 'login required', 'is_authenticated': False, 'token': None})
        except Exception as why:
            return errors.DOES_NOT_EXIST


class Logout(Resource):
    """
    Author: AtharvaCM
    POST:
        desc:
            logs the user out and invalidates the token
        body:
            - user_id
    """

    @token_required
    def post(self, token):
        # get params from request body
        try:
            user_id = request.json.get("user_id")
        except Exception as why:
            # Log input strip or etc. errors.
            print("input is wrong. " + str(why))
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # if user_id is None
        if user_id is None:
            # Return invalid input error.
            return errors.INVALID_INPUT_422

        # logout
        session['logged_in'] = False

        return jsonify(dict(is_authenticated=False, status="invalidated"))


api = Api(auth)
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Register, '/register')
