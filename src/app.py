import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS

from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db, User, Character, Planet

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    return jsonify({"msg": "Hello, this is your GET /user response"}), 200


@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get(people_id)
    if not person:
        raise APIException('Character not found', status_code=404)
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.first()
    if not user:
        raise APIException('User not found', status_code=404)

    favorites = {
        'favorite_characters': [c.serialize() for c in user.favorite_characters],
        'favorite_planets':    [p.serialize() for p in user.favorite_planets],
    }
    return jsonify(favorites), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.first()
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    if planet in user.favorite_planets:
        raise APIException('Planet already in favorites', status_code=400)
    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify({'message': f'Planet {planet.name} added to favorites'}), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user = User.query.first()
    person = Character.query.get(people_id)
    if not person:
        raise APIException('Character not found', status_code=404)
    if person in user.favorite_characters:
        raise APIException('Character already in favorites', status_code=400)
    user.favorite_characters.append(person)
    db.session.commit()
    return jsonify({'message': f'Character {person.name} added to favorites'}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user = User.query.first()
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    if planet not in user.favorite_planets:
        raise APIException('Planet not in favorites', status_code=400)
    user.favorite_planets.remove(planet)
    db.session.commit()
    return jsonify({'message': f'Planet {planet.name} removed from favorites'}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_person(people_id):
    user = User.query.first()
    person = Character.query.get(people_id)
    if not person:
        raise APIException('Character not found', status_code=404)
    if person not in user.favorite_characters:
        raise APIException('Character not in favorites', status_code=400)
    user.favorite_characters.remove(person)
    db.session.commit()
    return jsonify({'message': f'Character {person.name} removed from favorites'}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
