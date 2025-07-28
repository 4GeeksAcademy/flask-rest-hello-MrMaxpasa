from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

# Association tables using core Column objects
user_planet_favorites = Table(
    'user_planet_favorites',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('planet_id', Integer, ForeignKey('planet.id'), primary_key=True),
)

user_character_favorites = Table(
    'user_character_favorites',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('character.id'), primary_key=True),
)

user_vehicle_favorites = Table(
    'user_vehicle_favorites',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('vehicle_id', Integer, ForeignKey('vehicle.id'), primary_key=True),
)

character_vehicle_association = Table(
    'character_vehicle_association',
    db.Model.metadata,
    Column('character_id', Integer, ForeignKey('character.id'), primary_key=True),
    Column('vehicle_id', Integer, ForeignKey('vehicle.id'), primary_key=True),
)

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    subscription_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    favorite_planets = relationship(
        'Planet',
        secondary=user_planet_favorites,
        back_populates='fans',
    )
    favorite_characters = relationship(
        'Character',
        secondary=user_character_favorites,
        back_populates='fans',
    )
    favorite_vehicles = relationship(
        'Vehicle',
        secondary=user_vehicle_favorites,
        back_populates='fans',
    )

    posts = relationship('Post', back_populates='author')

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'subscription_date': self.subscription_date.isoformat(),
        }

class Planet(db.Model):
    __tablename__ = 'planet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(100))
    terrain: Mapped[str] = mapped_column(String(100))
    population: Mapped[str] = mapped_column(String(50))

    fans = relationship(
        'User',
        secondary=user_planet_favorites,
        back_populates='favorite_planets',
    )
    residents = relationship('Character', back_populates='origin_planet')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'climate': self.climate,
            'terrain': self.terrain,
            'population': self.population,
        }

class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(20))
    birth_year: Mapped[str] = mapped_column(String(20))
    origin_planet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('planet.id'), nullable=True
    )
    origin_planet = relationship('Planet', back_populates='residents')

    fans = relationship(
        'User',
        secondary=user_character_favorites,
        back_populates='favorite_characters',
    )
    vehicles = relationship(
        'Vehicle',
        secondary=character_vehicle_association,
        back_populates='pilots',
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'birth_year': self.birth_year,
            'origin_planet': self.origin_planet.name if self.origin_planet else None,
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100))
    manufacturer: Mapped[str] = mapped_column(String(100))
    cost_in_credits: Mapped[str] = mapped_column(String(50))
    length: Mapped[str] = mapped_column(String(50))
    crew: Mapped[str] = mapped_column(String(50))
    passengers: Mapped[str] = mapped_column(String(50))
    vehicle_class: Mapped[str] = mapped_column(String(50))

    fans = relationship(
        'User',
        secondary=user_vehicle_favorites,
        back_populates='favorite_vehicles',
    )
    pilots = relationship(
        'Character',
        secondary=character_vehicle_association,
        back_populates='vehicles',
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'cost_in_credits': self.cost_in_credits,
            'length': self.length,
            'crew': self.crew,
            'passengers': self.passengers,
            'vehicle_class': self.vehicle_class,
        }

class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    author = relationship('User', back_populates='posts')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': f'{self.author.first_name} {self.author.last_name}',
        }
