from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from models.user import User, Pictures
from models.follows import Follows
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


following_blueprint = Blueprint('following',
                            __name__,
                            template_folder='templates')

@following_blueprint.route('/follow/<id>', methods=['POST'])
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


@following_blueprint.route('/unfollow/<id>', methods=['POST'])
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


@following_blueprint.route('/requests')
def follower_request():
    return render_template('users/requests.html')


@following_blueprint.route('/requests/<id>', methods=['POST'])
def approve_requests(id):
    approved = Follows.update(is_approved=True).where((Follows.fan_id == id) & (Follows.idol_id == current_user.id))
    if approved.execute():
        return redirect(url_for('following.follower_request'))


@following_blueprint.route('/reject/<id>', methods=['POST'])
def reject_requests(id):
    rejected = Follows.delete().where((Follows.fan_id == id) & (Follows.idol_id == current_user.id))
    if rejected.execute():
        return redirect(url_for('following.follower_request'))
