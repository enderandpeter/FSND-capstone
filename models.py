import os
from sqlalchemy import Column, String, Integer, DateTime, Enum
from flask_sqlalchemy import SQLAlchemy
import json
import enum

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
    binds a flask application and a SQLAlchemy service
    :param app:
    :param database_path:
    :return:
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


actors_movies = db.Table(
    'actors_movies',
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True)
)


class Movies(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(DateTime)
    actors = db.relationship(
        'Actors',
        secondary=actors_movies,
        lazy='subquery',
        backref=db.backref('movies', lazy=True)
    )

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.strftime('%c')
        }


class Actors(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(Enum('m', 'f', name='gender'))

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': 'Male' if self.gender is 'm' else 'Female'
        }
