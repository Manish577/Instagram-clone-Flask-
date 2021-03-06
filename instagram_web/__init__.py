from myproject import app
from flask import render_template
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.pictures.views import pictures_blueprint
from instagram_web.blueprints.donations.views import donations_blueprint
from instagram_web.blueprints.following.views import following_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models.user import Pictures, User

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(pictures_blueprint, url_prefix="/pictures")
app.register_blueprint(donations_blueprint, url_prefix="/donations")
app.register_blueprint(following_blueprint, url_prefix="/following")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def home():
    user = User.select().prefetch(Pictures)
    return render_template('home.html',user=user)

