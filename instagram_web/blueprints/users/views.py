from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from models.user import User, Pictures
from models.follows import Follows
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    password_error = []
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    description = request.form.get('description')
    status = request.form.get('signup-status')

    taken = False
    check_username = User.get_or_none(User.username == username)
    check_email = User.get_or_none(User.email == email)
    if check_email or check_username:
        taken = True

    if taken:
        flash('Username or email taken. Please try again.')
        return render_template('users/new.html', errors=password_error)

    if password != confirm_password:
        password_error.append(
            'PLEASE MAKE SURE CONFIRM PASSORD FIELD IS EQUAL TO PASSWORD FIELD. PLEASE TRY AGAIN.')
        return render_template('users/new.html', errors=password_error)

    if status == "private":
        status = "Private"
    else:
        status = "Public"

    new_user = User(name=name, username=username, email=email,
                    password=password, description=description, status=status)

    if new_user.save():
        login_user(new_user)
        return redirect(url_for('home', username=new_user.username))
    else:
        return render_template('users/new.html', username=request.form.get('username'), email=request.form.get('email'), errors=new_user.errors)


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pictures = Pictures.select()
    user = User.get_or_none(User.username == username)
    if user:
        return render_template('users/username.html', user=user, pictures=pictures)
    else:
        flash('User not found. Please be aware that username is case sensitive.')
        return render_template('users/search-error.html')


@users_blueprint.route('/profile', methods=["POST"])
def show_user():
    username = request.form.get('searched-name')
    return redirect(url_for('users.show', username=username))


@users_blueprint.route('/sign_out', methods=["POST"])
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('sessions.sign_in'))


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/edit', methods=['GET'])
@login_required
def edit():
    return render_template('users/edit.html')


@users_blueprint.route('/update', methods=['POST'])
@login_required
def update():
    username = request.form.get('username')
    name = request.form.get('name')
    email = request.form.get('email')
    description = request.form.get('description')
    status = request.form.get('status')
    taken = False

    check_username = User.get_or_none(User.username == username)
    check_email = User.get_or_none(User.email == email)
    if check_email or check_username:
        taken = True

    if taken:
        flash('Username or email is taken. Please try again.')
        return redirect(url_for('users.edit'))

    if not username:
        username = current_user.username
    if not name:
        name = current_user.name
    if not email:
        email = current_user.email
    if not description:
        description = current_user.description
    if status == "private":
        status = "Private"
    else:
        status = "Public"
    User.update(name=name, username=username, email=email, description=description, status=status).where(
        User.id == current_user.id).execute()

    return redirect(url_for('users.edit'))


@users_blueprint.route('/directory')
def directory():
    users = User.select().where(User.status == 'Public')
    return render_template('users/directory.html', users=users)


@users_blueprint.route('/follow/<id>', methods=['POST'])
def follow(id):
    # do your stuffs, talk db
    idol = User.get_by_id(id)
    if idol.status == "Public":
        i = Follows(idol_id=id, fan_id=current_user.id, is_approved=True)
    else:
        i = Follows(idol_id=id, fan_id=current_user.id, is_approved=False)
        message = Mail(
            from_email='nextagram@example.com',
            to_emails=idol.email,
            subject='Following Request Notification',
            html_content='@' + current_user.username + ' wants to follow you.')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))
    followers = Follows.select().where(Follows.idol_id == id).count()
    if i.save():
        if i.is_approved == False:
            return jsonify({
                'success': True,
                'pending': True,
            })
        elif i.is_approved == True:
            return jsonify({
                'success': True,
                'pending': False,
                'followers': int(followers) + 1
            })


@users_blueprint.route('/unfollow/<id>', methods=['POST'])
def unfollow(id):
    i = Follows.delete().where((Follows.idol_id == id) &
                               (current_user.id == Follows.fan_id))
    private_container = render_template('private-container.html')
    followers = Follows.select().where(Follows.idol_id == id).count()
    user = User.get_by_id(id)
    if i.execute():
        if user.status == "Public":
            return jsonify({
                'success': True,
                'followers': int(followers) - 1,
                'status': True
            })
        else:
            return jsonify({
                'success': True,
                'followers': int(followers) - 1,
                'status': False,
                'private_container': private_container
            })


@users_blueprint.route('/requests')
def follower_request():
    return render_template('following/requests.html')


@users_blueprint.route('/requests/<id>', methods=['POST'])
def approve_requests(id):
    approved = Follows.update(is_approved=True).where(
        (Follows.fan_id == id) & (Follows.idol_id == current_user.id))
    if approved.execute():
        return redirect(url_for('users.follower_request'))


@users_blueprint.route('/reject/<id>', methods=['POST'])
def reject_requests(id):
    rejected = Follows.delete().where((Follows.fan_id == id) &
                                      (Follows.idol_id == current_user.id))
    if rejected.execute():
        return redirect(url_for('users.follower_request'))
