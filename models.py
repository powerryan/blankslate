from __main__ import app, db
from sqlalchemy import ForeignKey
from flask_login import UserMixin
import uuid
import sqlalchemy

class Player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomCode = db.Column(db.String(5))
    name = db.Column(db.String(255))
    points = db.Column(db.Integer)
    answer = db.Column(db.String(255))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompts = db.Column(db.String(255))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():

    #Player.__table__.drop(db.engine)
    db.create_all()
