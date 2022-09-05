from src.database import db
from datetime import datetime

amenity_hotel = db.Table(
    'amenity_hotel',
    db.Column('amenity', db.Integer, db.ForeignKey(
        'amenity.id'), primary_key=True),
    db.Column('hotel', db.Integer, db.ForeignKey(
        'hotel.id'), primary_key=True),
)

hotel_extra_feature = db.Table(
    'hotel_extra_feature',
    db.Column('hotel', db.Integer, db.ForeignKey(
        'hotel.id'), primary_key=True),
    db.Column('extra_feature', db.Integer, db.ForeignKey(
        'feature.id'), primary_key=True),
)


class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return f'Amenities>>>{self.type}'

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    ratings = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.ARRAY(db.String(50)), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    features = db.Column(db.ARRAY(db.String(50)), nullable=False)
    room_images = db.Column(db.ARRAY(db.String(255)), nullable=False)
    hotel_dp = db.Column(db.String(255), nullable=False) 
    amenities = db.relationship('Amenities', secondary=amenity_hotel, backref='hotel')
    extra_feature = db.relationship('extra_feature', secondary=hotel_extra_feature, backref='hotel') 
    

    def serialize(self):
        pass

    def __repr__(self) -> str:
        return f'Hotel>>>{self.name}'

class Room(db.model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    capacity_per_room = db.Column(db.Integer, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.Array(db.String(120)), nullable=False)
    hotel = db.relationship('Hotel', backref='room')
    
    
    def __repr__(self) -> str:
        return f'Room>>>{self.type}'
    

class Booking(db.model):
    booking_code = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50), nullable=False)
    check_in_date = db.Column(db.DateTime, default=datetime.now())
    check_out_date = db.Column(db.DateTime, default=datetime.now())
    amount = db.Column(db.Integer(50), nullable=False)
    payment = db.Column(db.String(120), nullable=False)
    number_of_rooms = db.Column(db.Integer, nullable=False)
    booking_Date = db.Column(db.DateTime, default=datetime.now())
    travelers = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now())
    updated_on = db.Column(db.DateTime(), default=datetime.now())
    room = db.relationship('Room', backref='Booking')
    user = db.relationship('User', backref='Booking')
    
    
    def __repr__(self) -> str:
        return f'Booking>>>{self.booking_code}'
    
    
class Extra_feature(db.model):
    hotel_id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, primary_key=True)
    comp_key = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    
    
    def __repr__(self) -> str:
        return f'Extra_feature>>>{self.type}'
    
    
class User_search(db.model):
    user_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    search_count = db.Column(db.Integer, nullable=False)
    comp_key = db.Column(db.String(120), nullable=False)
    user = db.relationship('User', backref='user_search')
    hotel = db.relationship('Hotel', backref='user_search')
    
    
    def __repr__(self) -> str:
        return f'user_search>>>{self.city}'
    
    
class Booking_feature(db.model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)
    booking = db.relationship('booking', backref='booking_feature')


    def __repr__(self) -> str:
        return f'Booking_feature>>>{self.type}'
    

class Review(db.model):
    user_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    review_date = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.column(db.String(255), nullable=False)
    hotel = db.relationship('hotel', backref='review')
    user = db.relationship('user', backref='review')
    
    
    def __repr__(self) -> str:
        return f'Review>>>{self.comment}'
