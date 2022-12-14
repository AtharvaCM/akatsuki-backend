from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS

import os

from flasgger import Swagger
from src.config.swagger import template, swagger_config

# blueprints
from src.api.auth.auth import auth
from src.api.booking.booking import booking
from src.api.hotel.hotel import hotel
from src.api.recommendation.recommendation import recommendation

from src.database import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SWAGGER={
                'title': "Hotel Booking API",
                'uiversion': 3,
            }
        )
    else:
        app.config.from_mapping(test_config)

    # db init
    db.app = app
    db.init_app(app)

    # CORS Config
    CORS(app)

    #  register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(hotel)
    app.register_blueprint(booking)
    app.register_blueprint(recommendation)

    Swagger(app, config=swagger_config, template=template)

    return app
