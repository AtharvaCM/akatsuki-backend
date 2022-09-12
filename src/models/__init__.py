from datetime import datetime
import json

from sqlalchemy import not_

# DB
from src.database import db


class Model(db.Model):
    __abstract__ = True

    # Stores changes made to this model's attributes. Can be retrieved
    # with model.changes
    _changes = {}

    def __init__(self, **kwargs):
        kwargs['_force'] = True
        self._set_columns(**kwargs)

    def _set_columns(self, **kwargs):
        force = kwargs.get('_force')

        readonly = []
        if hasattr(self, 'readonly_fields'):
            readonly = self.readonly_fields
        if hasattr(self, 'hidden_fields'):
            readonly += self.hidden_fields

        readonly += [
            'id',
            'created',
            'updated',
            'modified',
            'created_at',
            'updated_at',
            'modified_at',
        ]

        changes = {}

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()

        for key in columns:
            allowed = True if force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    changes[key] = {'old': val, 'new': kwargs[key]}
                    setattr(self, key, kwargs[key])

        for rel in relationships:
            allowed = True if force or rel not in readonly else False
            exists = True if rel in kwargs else False
            if allowed and exists:
                is_list = self.__mapper__.relationships[rel].uselist
                if is_list:
                    valid_ids = []
                    query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    for item in kwargs[rel]:
                        if 'id' in item and query.filter_by(id=item['id']).limit(1).count() == 1:
                            obj = cls.query.filter_by(id=item['id']).first()
                            col_changes = obj.set_columns(**item)
                            if col_changes:
                                col_changes['id'] = str(item['id'])
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(item['id']))
                        else:
                            col = cls()
                            col_changes = col.set_columns(**item)
                            query.append(col)
                            db.session.flush()
                            if col_changes:
                                col_changes['id'] = str(col.id)
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(col.id))

                    # delete related rows that were not in kwargs[rel]
                    for item in query.filter(not_(cls.id.in_(valid_ids))).all():
                        col_changes = {
                            'id': str(item.id),
                            'deleted': True,
                        }
                        if rel in changes:
                            changes[rel].append(col_changes)
                        else:
                            changes.update({rel: [col_changes]})
                        db.session.delete(item)

                else:
                    val = getattr(self, rel)
                    if self.__mapper__.relationships[rel].query_class is not None:
                        if val is not None:
                            col_changes = val.set_columns(**kwargs[rel])
                            if col_changes:
                                changes.update({rel: col_changes})
                    else:
                        if val != kwargs[rel]:
                            setattr(self, rel, kwargs[rel])
                            changes[rel] = {'old': val, 'new': kwargs[rel]}

        return changes

    def set_columns(self, **kwargs):
        self._changes = self._set_columns(**kwargs)
        if 'modified' in self.__table__.columns:
            self.modified = datetime.utcnow()
        if 'updated' in self.__table__.columns:
            self.updated = datetime.utcnow()
        if 'modified_at' in self.__table__.columns:
            self.modified_at = datetime.utcnow()
        if 'updated_at' in self.__table__.columns:
            self.updated_at = datetime.utcnow()
        return self._changes

    @property
    def changes(self):
        return self._changes

    def reset_changes(self):
        self._changes = {}

    def to_dict(self, show=None, hide=None, path=None, show_all=None):
        """ Return a dictionary representation of this model.
        """

        if not show:
            show = []
        if not hide:
            hide = []
        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields
        default = []
        if hasattr(self, 'default_fields'):
            default = self.default_fields

        ret_data = {}

        if not path:
            path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                item = '%s%s' % (path, item)
                return item
            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is 'id' or check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    ret_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(item.to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        ))
                else:
                    if self.__mapper__.relationships[key].query_class is not None:
                        ret_data[key] = getattr(self, key).to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        )
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith('_'):
                continue
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                try:
                    ret_data[key] = json.loads(json.dumps(val))
                except:
                    pass

        return ret_data


def requested_columns(request):
    show = request.args.get('show', None)
    if not show:
        return []
    return show.split(',')


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


class User(Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    bookings = db.relationship('Booking', backref='user_booking')
    reviews = db.relationship('Review', backref='user_review')

    def __repr__(self) -> str:
        return f'{self.username}'

    default_fields = ['id', 'username', 'email',
                      'password', 'created_at', 'updated_at']


class Amenity(Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return f'{self.type}'

    default_fields = ['id', 'type']


class Hotel(Model):
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

    default_fields = ['id', 'name', 'address', 'description', 'ratings',
                      'tags', 'city', 'state', 'country', 'features', 'room_images', 'hotel_dp']


class Room(Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    capacity_per_room = db.Column(db.Integer, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    features = db.Column(db.ARRAY(db.String(120)), nullable=False)

    bookings = db.relationship('Booking', backref='room_booking')

    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

    def __repr__(self) -> str:
        return f'{self.room_type}'

    default_fields = ['id', 'cost', 'room_type', 'capacity_per_room',
                      'available_rooms', 'total_rooms', 'features']


class Booking(Model):
    booking_code = db.Column(db.String(120), primary_key=True)
    room_type = db.Column(db.String(50), nullable=False)
    check_in_date = db.Column(db.DateTime, default=datetime.now())
    check_out_date = db.Column(db.DateTime, default=datetime.now())
    amount = db.Column(db.Integer, nullable=False)
    payment = db.Column(db.String(120), nullable=False)
    number_of_rooms = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now())
    travelers = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now())
    updated_on = db.Column(db.DateTime(), default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    def __repr__(self) -> str:
        return f'{self.booking_code}'

    default_fields = ['booking_code', 'room_type', 'check_in_date',
                      'check_out_date', 'amount', 'payment', 'number_of_rooms',
                      'booking_date', 'travelers', 'created_at', 'updated_at']


class Extrafeature(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}'

    default_fields = ['id', 'name', 'cost']


class Review(Model):
    id = db.Column(db.Integer, primary_key=True)
    review_date = db.Column(
        db.DateTime(), nullable=False, default=datetime.now())
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)

    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f'{self.comment}'

    default_fields = ['id', 'review_date', 'rating', 'comment']
