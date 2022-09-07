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
    db.Column('extrafeature', db.Integer, db.ForeignKey(
        'extrafeature.id'), primary_key=True),
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    bookings = db.relationship('Booking', backref='user_booking')
    reviews = db.relationship('Review', backref='user_review')

    def __repr__(self) -> str:
        return f'{self.username}'


class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return f'{self.type}'

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

    rooms = db.relationship('Room', backref='hotel_room')
    bookings = db.relationship('Booking', backref='hotel_booking')
    reviews = db.relationship('Review', backref='hotel_review')

    amenities = db.relationship('Amenity', secondary=amenity_hotel,
                                lazy='subquery', backref=db.backref('hotels', lazy=True))
    extra_features = db.relationship(
        'Extrafeature', secondary=hotel_extra_feature, lazy='subquery', backref=db.backref('hotels', lazy=True))

    def __repr__(self) -> str:
        return f'{self.name}'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    capacity_per_room = db.Column(db.Integer, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    features = db.Column(db.ARRAY(db.String(120)), nullable=False)

    bookings = db.relationship('Booking', backref='room_booking')

    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

    db.UniqueConstraint(room_type, hotel_id)

    def __repr__(self) -> str:
        return f'{self.room_type}'

class Booking(db.Model):
    booking_code = db.Column(db.String(120), primary_key=True)
    check_in_date = db.Column(db.DateTime, default=datetime.now())
    check_out_date = db.Column(db.DateTime, default=datetime.now())
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(120), nullable=False)
    number_of_rooms = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now())
    travelers = db.Column(db.Integer, nullable=False)
    ts_created = db.Column(db.DateTime(), default=datetime.now())
    ts_updated = db.Column(db.DateTime(), default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    def __repr__(self) -> str:
        return f'{self.booking_code}'

class Extrafeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_date = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f'{self.comment}'
