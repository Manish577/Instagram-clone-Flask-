from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from instagram_web.helpers.google_oauth import oauth
import random
import string

sessions_blueprint = Blueprint('sessions',
                               __name__,
                               template_folder='templates')


@sessions_blueprint.route('/sign_in')
def sign_in():
    return render_template('sessions/new.html')


@sessions_blueprint.route('/sign_in', methods=["POST"])
def signed_in():
    input_username = request.form.get('username')
    input_password = request.form.get('password')
    user = User.get_or_none(User.username == input_username)
    if input_username or input_password:
        if user and check_password_hash(user.password, input_password):
            login_user(user)
            return redirect(url_for('users.show', username=user.username))
        else:
            flash('Invalid Login. Please try again.')
            return render_template('sessions/new.html')
    else:
        return render_template('sessions/new.html')


@sessions_blueprint.route("/google_login")
def google():
    return oauth.google.authorize_redirect(url_for('sessions.google_auth', _external=True))


@sessions_blueprint.route("/google_auth")
def google_auth():
    oauth.google.authorize_access_token()
    data = oauth.google.get(
        'https://www.googleapis.com/oauth2/v2/userinfo').json()
    user = User.get_or_none(User.email == data.get('email'))
    if user:
        login_user(user)
        return redirect(url_for('home'))
    else:
        name = data.get('name')
        username = name
        email = data.get('email')
        password = ''.join([random.choice(
            string.ascii_letters + string.digits + string.punctuation) for n in range(12)])
        description = ''
        new_user = User(name=name, username=username, email=email,
                        password=password, description=description)
        if new_user.save():
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please try again.')
            return render_template('sessions/new.html')
