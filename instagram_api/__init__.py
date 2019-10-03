import os
from instagram_api.blueprints.users.views import users_api_blueprint
from instagram_api.blueprints.images.views import images_api_blueprint
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_cors import CORS

web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')
app = Flask('NEXTAGRAM', root_path=web_dir)
csrf = CSRFProtect(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
csrf.exempt(users_api_blueprint)
csrf.exempt(images_api_blueprint)
## API Routes ##


app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(images_api_blueprint, url_prefix='/api/v1/images')
