from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from models.user import User, Pictures
from models.donation import Donation
import os
import boto3
import botocore
from app import s3
from flask_login import current_user
import braintree
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


donations_blueprint = Blueprint('donations',
                                __name__,
                                template_folder='templates')

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ.get('MERCHANT_ID'),
        public_key=os.environ.get('PUBLIC_KEY'),
        private_key=os.environ.get('PRIVATE_KEY')
    )
)


@donations_blueprint.route('/donations/<id>')
def new(id):
    client_token = gateway.client_token.generate()

    return render_template('donations/new.html', client_token=client_token, id=id)


@donations_blueprint.route('/checkout/<id>', methods=["POST"])
def create_purchase(id):
    nonce_from_the_client = request.form["this-input"]
    amount = request.form.get('this-amount')
    gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })
    Donation(amount=amount, image_id=id, donor_id=current_user.id).save()
    pic = Pictures.get_by_id(id)
    user = User.get_or_none(User.id == pic.user_id)
    username = user.username
    message = Mail(
        from_email='nextagram@example.com',
        to_emails=user.email,
        subject='Donation Notification',
        html_content='@' + current_user.username + ' donated ' + amount + f'$ to the following image below!<br><img src="{ pic.post_image }" />')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
    return redirect(url_for('users.show', username=username))
