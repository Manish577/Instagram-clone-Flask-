from flask import Blueprint, jsonify, request
from models.user import User
from models.user import Pictures
from flask_jwt_extended import (jwt_required, create_access_token,
                                get_jwt_identity
                                )


images_api_blueprint = Blueprint('images_api',
                                 __name__,
                                 template_folder='templates')


@images_api_blueprint.route('/user/<id>', methods=['GET'])
def index(id):
    images_arr = []
    for image in Pictures.select().where(Pictures.user_id == id):
        images_arr.append(image.post_image)

    return jsonify(images_arr)


@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    current_user_id = get_jwt_identity()
    images_arr = []
    for image in Pictures.select().where(Pictures.user_id == current_user_id):
        images_arr.append(image.post_image)

    return jsonify(images_arr)