from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Scara/PycharmProjects/Thermostat3/weatherdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
''''
sensor_identifier = db.Table('sensor_identifier', db.Column('sensor_id', db.Integer, db.ForeignKey('sensor.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120),  nullable=False)
    sensors = db.relationship("Sensor", secondary=sensor_identifier, lazy='subquery', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f"User('{self.username}','{self.password}')"
'''
class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True, nullable=False)
    room = db.Column(db.String(120), unique=True, nullable=False)
    measurements = db.relationship("Measurement", backref="sensor",
                                   cascade="all, delete, delete-orphan", lazy=True)

    def __repr__(self):
        return f"Sensor('{self.id},'{self.url}','{self.room}')"

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sensor_url = db.Column(db.String(120), db.ForeignKey('sensor.url'))   #o sensor_id??

    def __repr__(self):
        return f"Measurement('{self.temperature}','{self.humidity}')"


