# Hotel blueprint
# All hotel related API will be maintained here

from flask import Blueprint

hotel = Blueprint("hotel", __name__, url_prefix="api/v1/hotel")