from instagram_api.blueprints.users.views import users_api_blueprint
from instagram_api.blueprints.images.views import images_api_blueprint
from app import csrf, app
from flask_cors import CORS

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
csrf.exempt(users_api_blueprint)
csrf.exempt(images_api_blueprint)
## API Routes ##


app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(images_api_blueprint, url_prefix='/api/v1/images')
