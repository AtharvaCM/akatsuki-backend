from src.database import db

amenities_hotel = db.Table(
    db.Column('amenities_id', db.Integer,db.ForeignKey('amenities.id')),
    db.Column('hotel_id', db.Integer,db.ForeignKey('hotel.id')),
)

class Amenities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return 'Amenities>>>{self.type}'

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
    amenities = db.relationship('Amenities', secondary=amenities_hotel, backref='types')

    def __repr__(self) -> str:
        return 'Hotel>>>{self.name}'


