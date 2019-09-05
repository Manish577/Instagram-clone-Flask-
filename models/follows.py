from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from flask import request
from playhouse.hybrid import hybrid_property
import os
from models.user import User


class Follows(BaseModel):
    idol = pw.ForeignKeyField(User, backref='fans')
    fan = pw.ForeignKeyField(User, backref='idols')
    is_approved = pw.BooleanField(null=True)
