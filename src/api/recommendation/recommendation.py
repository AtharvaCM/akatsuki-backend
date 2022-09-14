from datetime import datetime
from email import message
import json
from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse

from flasgger import swag_from
from sqlalchemy.sql import func

from src.database import db

# importing Model
from src.models import Usercitysearch, User, requested_columns

# error codes
from src.api.error import errors

recommendation = Blueprint("recommendation", __name__, url_prefix="/api/v1/recommendation")
api = Api(recommendation)

parser = reqparse.RequestParser()

class CityRecommendList(Resource):
    def get(self, id):

        city = db.session.query(Usercitysearch
                                ).filter(Usercitysearch.search_count >=5
                                         ).filter(Usercitysearch.user_id == id).all()

        show = requested_columns(request)
        city_serialized = []
        
        for loc in city:
            city_serialized.append(loc.to_dict(show=show))
            
        return jsonify(dict(data=city_serialized))

    def post(self, id):
        city = 'Manali' #request.args.get('city', type=str)
        
        # check if city already exists based on search
        citysearch = Usercitysearch.query.filter(db.and_(Usercitysearch.user_id == id, 
                    Usercitysearch.city == city)).first()
        
        if citysearch is not None:
            count = citysearch.search_count +1
            print(count)
            setattr(citysearch, 'search_count', count)
            #db.session.add(cityrecordupdate)
            db.session.commit()
            return jsonify(dict(status="City record updated successfully"))
        else:
            # Create new record for that city
            cityrecord = Usercitysearch(city=city, search_count=1,user_id=id)
            db.session.add(cityrecord)
            db.session.commit()
            return jsonify(dict(status="City record added successfully"))


api.add_resource(CityRecommendList, '/locations/<int:id>')