import uuid
from flask_login import UserMixin
from .. import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(1000), nullable=False)
    address = db.Column(db.String(1000), default="-")
    photo = db.Column(db.String(1000), default="-")

    user_id = db.Column(db.String(150), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

class Time(db.Model):
    __tablename__ = 'times'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    time = db.Column(db.String(1000), default="-")

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(1000), nullable=False)
    photo = db.Column(db.String(1000), default="-")
    telp = db.Column(db.String(1000), default="-")
    time = db.Column(db.String(1000), default="-")
    date = db.Column(db.String(1000), default="-")
    information = db.Column(db.String(1000), default="-")

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    telp = db.Column(db.String(1000), default="-")
    time = db.Column(db.String(1000), default="-")
    date = db.Column(db.Date)
    status = db.Column(db.String(1000), default="-")
    customer_id = db.Column(db.String(150), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.String(150), db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)

    spcustomer = db.relationship('User', backref='bookings')
    spdoctor = db.relationship('Doctor', backref='bookings')

class TypeTreatment(db.Model):
    __tablename__ = 'type_treatments'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String(1000), default="-")

class Treatment(db.Model):
    __tablename__ = 'treatments'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    treatment = db.Column(db.String(1000), default="-")
    benefit = db.Column(db.String(1000), default="-")
    skin = db.Column(db.String(1000), default="-")
    information = db.Column(db.String(1000), default="-")
    type_id = db.Column(db.String(150), db.ForeignKey('type_treatments.id', ondelete='CASCADE'), nullable=False)

    types = db.relationship('TypeTreatment', backref='treatments')