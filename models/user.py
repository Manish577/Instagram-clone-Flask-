from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from flask import request
from playhouse.hybrid import hybrid_property
import os
from flask_login import current_user
from enum import Enum


class User(BaseModel, UserMixin):
    name = pw.CharField(null=False)
    username = pw.CharField(unique=True, null=False)
    email = pw.TextField(unique=True, null=False)
    password = pw.TextField(null=False)
    description = pw.TextField(null=True)
    profile_picture = pw.TextField(null=True)
    status = pw.TextField(null=True)

    def num_of_image(self, count=-1):
        return [x for x in Pictures.select().where(Pictures.user_id == self.id).order_by(Pictures.created_at.desc())[0:count]]

    @hybrid_property
    def ordering(self):
        return [x for x in Pictures.select().where(Pictures.user_id == self.id).order_by(Pictures.created_at.desc())]

    @hybrid_property
    def follower(self):
        from models.follows import Follows
        return [x.fan for x in Follows.select().where((Follows.idol_id == self.id) & (Follows.is_approved == True))]

    @hybrid_property
    def following(self):
        from models.follows import Follows
        return [x.idol for x in Follows.select().where((Follows.fan_id == self.id) & (Follows.is_approved == True))]

    @hybrid_property
    def following_request(self):
        from models.follows import Follows
        return [x.idol for x in Follows.select().where((Follows.fan_id == self.id) & (Follows.is_approved == False))]

    
    @hybrid_property
    def follower_request(self):
        from models.follows import Follows
        return [x.fan for x in Follows.select().where((Follows.idol_id == self.id) & (Follows.is_approved == False))]

    @hybrid_property
    def profile_image_path(self):
        if self.profile_picture:
            return f'https://{os.environ.get("BUCKET-NAME")}.s3-ap-southeast-1.amazonaws.com/' + self.profile_picture
        else:
            return f'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'

    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)
        if duplicate_username:
            self.errors.append(
                'USERNAME NOT UNIQUE, FAILED TO CREATE NEW USER. PLEASE TRY AGAIN.')

        duplicate_email = User.get_or_none(User.email == self.email)
        if duplicate_email:
            self.errors.append(
                'EMAIL NOT UNIQUE, FAILED TO CREATE NEW USER. PLEASE TRY AGAIN.')

        pattern = re.match(
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*_=+-]).{6,99}$', self.password)
        if (len(self.password) > 6) and pattern:
            self.password = generate_password_hash(self.password)
        else:
            self.errors.append(
                'PLEASE ENTER VALID PASSWORD. PLEASE TRY AGAIN.')


class Pictures(BaseModel):
    user = pw.ForeignKeyField(User, backref='pictures')
    picture = pw.CharField(null=True)

    @hybrid_property
    def post_image(self):
        if self.picture:
            return f'https://{os.environ.get("BUCKET-NAME")}.s3-ap-southeast-1.amazonaws.com/' + self.picture
        else:
            return 'Upload unsuccessful'
