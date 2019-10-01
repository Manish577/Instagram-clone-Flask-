from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from models.user import User, Pictures
import os
import boto3
import botocore
from app import s3
from flask_login import current_user

pictures_blueprint = Blueprint('pictures',
                               __name__,
                               template_folder='templates')


@pictures_blueprint.route('/profile_image')
def upload():
    return render_template('pictures/new.html')


@pictures_blueprint.route('/profile_image', methods=["POST"])
def uploaded():
    user_file = request.files.get('user_file')
    try:
        s3.upload_fileobj(
            user_file,
            os.environ.get("BUCKET-NAME"),
            user_file.filename,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": user_file.content_type
            }
        )
        User.update(profile_picture=user_file.filename).where(
            User.id == current_user.id).execute()
    except:
        flash('Profile picture upload unsuccessful')

    return redirect(url_for('users.edit'))


@pictures_blueprint.route('/upload_image', methods=["POST"])
def create():
    picture = request.files.get('picture')
    try:
        s3.upload_fileobj(
            picture,
            os.environ.get("BUCKET-NAME"),
            picture.filename,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": picture.content_type
            }
        )
        Pictures(picture=picture.filename,user=current_user.id).save()
    except:
        flash('Upload unsuccessful')
        
    return redirect(url_for('users.show', username=current_user.username))

