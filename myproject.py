import os
import config
from flask import Flask, redirect, url_for, flash
from models.base_model import db
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from models.user import User
import boto3
import botocore
from flask_jwt_extended import JWTManager
from instagram_api.blueprints.users.views import users_api_blueprint


web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)
csrf = CSRFProtect(app)
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("S3-KEY-ID"),
    aws_secret_access_key=os.environ.get("S3-SECRET-KEY")
)


login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)



@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")


@app.before_request
def before_request():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc


@login_manager.unauthorized_handler
def unauthorized():
    flash('Please log in')
    return redirect(url_for('sessions.sign_in'))
