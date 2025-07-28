# models.py
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), nullable=False)  # A = Available, O = Occupied
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id= db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    vehicle_number = db.Column(db.String(20), nullable=False)
    user_deleted = db.Column(db.Boolean, default=False)
    spot = db.relationship('ParkingSpot', backref=db.backref('reservations', passive_deletes=True))

