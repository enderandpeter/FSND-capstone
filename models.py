import os
import json
from sqlalchemy import Column, String, Integer, DateTime, Enum, text, SmallInteger, CheckConstraint
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()
MIN_ACTOR_AGE = 0
MAX_ACTOR_AGE = 150
MIN_ACTOR_NAME_LENGTH = 3
MAX_ACTOR_NAME_LENGTH = 100
MIN_MOVIE_TITLE_LENGTH = 1
MAX_MOVIE_TITLE_LENGTH = 100

def setup_db(app, database_path=database_path):
    """
    binds a flask application and a SQLAlchemy service
    :param app:
    :param database_path:
    :return:
    """
    migrate = Migrate(app, db)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

    return db


def update():
    """
    updates a new model for the database
    EXAMPLE
        actor = Actors.query.filter(Actors.id == id).one_or_none()
        actor.name = 'Ursula McGuinn'
        actor.update()
    """
    db.session.commit()


class Model:
    def insert(self):
        """
        inserts a new model into the database
        Check the required attributes
        EXAMPLE
            actor = Actor(name="Jackie Underwood", gender='f', age=30)
            actor.insert()
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            actor = Actor(name="Greg Coriander")
            actor.delete()
        """
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {}

    def __repr__(self):
        return json.dumps(self.format())


actors_movies = db.Table(
    'actors_movies',
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id', onupdate='CASCADE', ondelete='CASCADE'),
              primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id', onupdate='CASCADE', ondelete='CASCADE'),
              primary_key=True)
)


class Movies(Model, db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    release_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
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
            'release_date': self.release_date.strftime('%c'),
            'actors': [{
                'id': actor.id,
                'name': actor.name,
                'gender': 'Male' if actor.gender is 'm' else 'Female',
                'age': actor.age
            } for actor in self.actors]
        }


class Actors(Model, db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_ACTOR_NAME_LENGTH), nullable=False)
    gender = Column(Enum('m', 'f', name='gender'), nullable=False, server_default='m')
    age = Column(SmallInteger, CheckConstraint(f'age > {MIN_ACTOR_AGE} AND age < {MAX_ACTOR_AGE}'), nullable=False)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': 'Male' if self.gender is 'm' else 'Female',
            'age': self.age,
            'movies': [{
                'id': movie.id,
                'title': movie.title,
                'release_date': movie.release_date.strftime('%c')
            } for movie in self.movies]
        }
