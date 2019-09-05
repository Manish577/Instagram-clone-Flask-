from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from flask import request
from playhouse.hybrid import hybrid_property
import os
from models.user import Pictures,User


class Donation(BaseModel):
    image = pw.ForeignKeyField(Pictures, backref='donations')
    donor = pw.ForeignKeyField(User, null=False, backref='donations')
    amount = pw.DecimalField(null=False, decimal_places=2)

