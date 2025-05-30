"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorite
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#GET: All
@app.route('/users', methods=['GET'])
def get_users():
    all_users = db.session.execute(db.select(User)).scalars().all()
    all_users= list(map(lambda item: item.serialize(),all_users))

    return {"users": all_users, "count": len(all_users)}, 200

@app.route('/planets', methods= ['GET'])
def get_planets():
    all_planets = db.session.execute(db.select(Planets)).scalars().all()
    all_planets= list(map(lambda item: item.serialize(), all_planets))

    return {"planets": all_planets, "count": len(all_planets)}, 200

@app.route('/people', methods= ['GET'])
def get_people():
    all_people = db.session.execute(db.select(People)).scalars().all()
    all_people = list(map(lambda item: item.serialize(),all_people))

    return {"people": all_people, "count": len(all_people)}, 200

#GET: ById
@app.route('/users/<int:user_id>')
def get_user_by_id(user_id):
    user_result = db.session.execute(db.select(User).where(User.id == user_id)).scalar_one_or_none()

    if user_result is None:
        return {"message": f"No existe el usuario con el id {user_id}"}, 404
    
    return {"user": user_result.serialize()}, 200

@app.route('/planets/<int:planets_id>')
def get_planets_by_id(planets_id):
    planet_result = db.session.execute(db.select(Planets).where(Planets.id == planets_id)).scalar_one_or_none()

    if planet_result is None:
        return {"message": f"No existe el planeta con el id {planets_id}"}, 404
    
    return {"planets": planet_result.serialize()}, 200

@app.route('/people/<int:people_id>')
def get_people_by_id(people_id):
    people_result = db.session.execute(db.select(People).where(People.id == people_id)).scalar_one_or_none()

    if people_result is None:
        return {"message": f"No existe el planeta con el id {people_id}"}, 404
    
    return {"people": people_result.serialize()}, 200

#POST: Planet Favorite
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_planet_favorite(planet_id):
    body = request.get_json(silent=True)
    
    if body is None:
        return {"message": "Debes enviarme el body"}, 400

    if 'user_id' not in body:
        return {"message": "Debes ingresar el user_id"}, 400

    # Validar existencia del usuario
    user = db.session.execute(select(User).where(User.id == body['user_id'])).scalar_one_or_none()
    if user is None:
        return {"message": f"El user_id {body['user_id']} no existe."}, 404

    # Validar existencia del planeta
    planet = db.session.execute(select(Planets).where(Planets.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return {"message": f"El planet_id {planet_id} no existe."}, 404

    # Validar que no esté duplicado
    existing_fav = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == body['user_id'],
            Favorite.content_type == 'planet',
            Favorite.content_id == planet_id
        )
    ).scalar_one_or_none()

    if existing_fav:
        return {"message": "Este planeta ya está en favoritos"}, 409

    # Crear favorito
    favorite = Favorite(
        user_id=body['user_id'],
        content_type='planet',
        content_id=planet_id
    )
    db.session.add(favorite)
    db.session.commit()

    return {"message": f"El planet_id {planet_id} ha sido asignado al user_id {body['user_id']}"}, 201

#POST: People Favorite
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_people_favorite(people_id):
    body = request.get_json(silent=True)
    
    if body is None:
        return {"message": "Debes enviarme el body"}, 400

    if 'user_id' not in body:
        return {"message": "Debes ingresar el user_id"}, 400

    # Validar existencia del usuario
    user = db.session.execute(select(User).where(User.id == body['user_id'])).scalar_one_or_none()
    if user is None:
        return {"message": f"El user_id {body['user_id']} no existe."}, 404

    # Validar existencia people
    people = db.session.execute(select(People).where(People.id == people_id)).scalar_one_or_none()
    if people is None:
        return {"message": f"El people_id {people_id} no existe."}, 404

    # Validar que no esté duplicado
    existing_fav = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == body['user_id'],
            Favorite.content_type == 'people',
            Favorite.content_id == people_id
        )
    ).scalar_one_or_none()

    if existing_fav:
        return {"message": "Este personaje ya está en favoritos"}, 409

    # Crear favorito
    favorite = Favorite(
        user_id=body['user_id'],
        content_type='people',
        content_id=people_id
    )
    db.session.add(favorite)
    db.session.commit()

    return {"message": f"El people_id {people_id} ha sido asignado al user_id {body['user_id']}"}, 201

#DELETE: Planet Favorite
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    body = request.get_json(silent=True)

    if body is None:
        return {"message": "Debes enviarme el body"}, 400

    if 'user_id' not in body:
        return {"message": "Debes ingresar el user_id"}, 400

    # Validar existencia usuario
    user = db.session.execute(select(User).where(User.id == body['user_id'])).scalar_one_or_none()
    if user is None:
        return {"message": f"El user_id {body['user_id']} no existe."}, 404

    # Buscar favorito existente
    favorite = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == body['user_id'],
            Favorite.content_type == 'planet',
            Favorite.content_id == planet_id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return {"message": f"Este planeta no está en favoritos del user_id {body['user_id']}"}, 404

    # Eliminar favorito
    db.session.delete(favorite)
    db.session.commit()

    return {"message": f"El planet_id {planet_id} ha sido eliminado de los favoritos del user_id {body['user_id']}"}, 200

#DELETE: People Favorite
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    body = request.get_json(silent=True)

    if body is None:
        return {"message": "Debes enviarme el body"}, 400

    if 'user_id' not in body:
        return {"message": "Debes ingresar el user_id"}, 400

    # Validar existencia usuario
    user = db.session.execute(select(User).where(User.id == body['user_id'])).scalar_one_or_none()
    if user is None:
        return {"message": f"El user_id {body['user_id']} no existe."}, 404

    # Buscar favorito existente
    favorite = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == body['user_id'],
            Favorite.content_type == 'people',
            Favorite.content_id == people_id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return {"message": f"Este personaje no está en favoritos del user_id {body['user_id']}"}, 404

    # Eliminar favorito
    db.session.delete(favorite)
    db.session.commit()

    return {"message": f"El people_id {people_id} ha sido eliminado de los favoritos del user_id {body['user_id']}"}, 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
