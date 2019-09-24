from flask import Blueprint, jsonify, request
from models.user import User
from werkzeug.security import check_password_hash
from flask_jwt_extended import (jwt_required, create_access_token,
                                get_jwt_identity
                                )


users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')


@users_api_blueprint.route('/', methods=['GET'])
def index():
    user_arr = []
    for user in User.select():
        response = {
            'username': user.username,
            'id': user.id,
            'profile_picture': user.profile_picture
        }
        user_arr.append(response)
    return jsonify(user_arr)


@users_api_blueprint.route('/', methods=['POST'])
def new():
    user = User(
        name = request.json.get('name'),
        username = request.json.get('username'),
        email = request.json.get('email'),
        # description = request.json.get('description')
        # status = request.json.get('status')
        password = request.json.get('password')
    )
    if user.save():
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "jwt": access_token,
            })
    else:
        return jsonify(user.errors,{
            "status": "failed"
        }), 400


@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    return jsonify({
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "password": current_user.password
    })


@users_api_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.get_or_none(User.username == username)
    if user and check_password_hash(user.password, password):
        return jsonify({
            "jwt": create_access_token(identity=user.id),
            "username": user.username,
            "name": user.name,
            "message": "Successfully signed in."
        })
    else:
        return jsonify({
            "status": "Failed to sign in."
        }), 400


@users_api_blueprint.route('/<id>', methods=['GET'])
def find(id):
    user = User.get_by_id(id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "profileImage": user.profile_image_path
    })


@users_api_blueprint.route('/check_name/<username>', methods=['GET'])
def check_name(username):
    user_check = User.get_or_none(User.username == username)
    if user_check:
        return jsonify({
            "exists": True,
            "valid": False
        })
    else: 
        return jsonify({
            "exist": False,
            "valid": True
        })