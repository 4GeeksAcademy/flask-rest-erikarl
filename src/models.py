from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import date

db = SQLAlchemy()

film_people = db.Table(
    'film_people',
    db.Column('film_id', db.Integer, db.ForeignKey('films.id'), primary_key=True),
    db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True)
)

film_planets = db.Table(
    'film_planets',
    db.Column('film_id', db.Integer, db.ForeignKey('films.id'), primary_key=True),
    db.Column('planet_id', db.Integer, db.ForeignKey('planets.id'), primary_key=True)
)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    suscription_date: Mapped[date] = mapped_column(Date(), nullable=False)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name
            # do not serialize the password, its a security breach
        }
    
class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(120), nullable=False)
    terrain: Mapped[str] = mapped_column(String(120), nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)

    films: Mapped[List["Films"]] = relationship(secondary="film_planets", back_populates="planets")

class People(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(80), nullable=False)
    homeworld: Mapped[str] = mapped_column(String(120), nullable=False)

    films: Mapped[List["Films"]] = relationship(secondary= "film_people", back_populates= "people")

class Films(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    director: Mapped[str] = mapped_column(String(120),nullable=False)
    release_date: Mapped[str] = mapped_column(String(50))

    people: Mapped[List["People"]] = relationship(secondary="film_people", back_populates="films")
    planets: Mapped[List["Planets"]] = relationship(secondary="film_planets", back_populates="films")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "director": self.director,
            "release_date": self.release_date,
            "people": [person.name for person in self.people],
            "planets": [planet.name for planet in self.planets]
    }

class Favorite(db.Model):

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "planet", "person", "film" 
    content_id: Mapped[int] = mapped_column(nullable=False)  # ID del planet, person o film

    user = relationship("User", back_populates="favorites")