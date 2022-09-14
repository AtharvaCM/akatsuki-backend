# # auth blueprint
# # All auth related API will be maintained here

# import logging
# from urllib import request
# from flask import Blueprint
# from flask_restful import Resource, Api, abort, reqparse

# from src.database import db
# import src.api.error.errors as error

# auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


# # Dummy users list
# USERS = {
#     '1': {'name': 'John'},
#     '2': {'name': 'Wilma'},
#     '3': {'name': 'Fred'}
# }

# # A helper function


# def abort_if_todo_doesnt_exist(user_id):
#     if user_id not in USERS:
#         abort(404, message="User {} doesn't exist".format(user_id))


# parser = reqparse.RequestParser()
# parser.add_argument('name')


# class Login(Resource):
#     @staticmethod
#     def post(self):
#         try:
#             # get user email and password
#             username, email, password = (
#                 request.json.get('username').strip(),
#                 request.json.get('email').strip(),
#                 reqparse.json.get('password').strip(),
#             )
#         except Exception as why:
#             # Log input strip or etc. errors.
#             logging.info("Email or password is wrong. " + str(why))

#             # Return invalid input error.
#             return error.INVALID_INPUT_422

#         # Check if any field is none.
#         if username is None or password is None or email is None:
#             return error.INVALID_INPUT_422

#         # Get user if it is exists.
#         user = User.query.filter_by(email=email).first()

#         # Check if user is existed.
#         if user is not None:
#             return error.ALREADY_EXIST

#         # Create a new user.
#         user = User(username=username, password=password, email=email)

#         # Add user to session.
#         db.session.add(user)

#         # Commit session.
#         db.session.commit()

#         # Return success if registration is completed.
#         return {"status": "registration completed."}


# class User(Resource):
#     def get(self, user_id):
#         return USERS[user_id]


# class UserList(Resource):
#     def get(self):
#         return USERS


# api = Api(auth)
# api.add_resource(UserList, '/users')
# api.add_resource(User, '/users/<string:user_id>')





from flask import Flask, jsonify, make_response, request, Blueprint, session 
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from flask_restful import Resource, Api, abort, reqparse
from datetime import datetime

from src.database import db 
from src.models import User
import uuid
import jwt
import os

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

SECRET_KEY=os.environ.get("SECRET_KEY")



def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
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
        hashed_password = generate_password_hash(data.get('password'), method='sha256')
        
        new_user = User(id=data.get('id'), name=data.get('name'), username=data.get('username'),email=data.get('email'), password=hashed_password,avatar = data.get('avatar'), created_at=datetime.now(), updated_at=datetime.now())

        db.session.add(new_user) 
        db.session.commit()   
        return jsonify({'message': 'registered successfully'})



class Login(Resource):
    def post(self):
        
        auth = request.json

        if not auth and not auth.get("username") or not auth.get("password") : 
            return jsonify({'Authentication': 'login required','is_authenticate': False,'token' : None})   
        user = User.query.filter_by(username=auth.get("username")).first()  
        print(user.password)
        print(auth.get("password"))
        # if user.password == auth.get("password"):
        if check_password_hash(user.password, auth.get("password")):
            session['logged_in'] = True
            token = jwt.encode({'id' : user.id}, SECRET_KEY, "HS256")
        
            return jsonify({'token' : token, 'is_authenticate': True}, 200)
        
        return jsonify({'Authentication': 'login required','is_authenticate': False,'token' : None})

api = Api(auth)
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
