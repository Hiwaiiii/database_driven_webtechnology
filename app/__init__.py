from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register web routes
    from app.routes import register_routes
    register_routes(app)

    # Register API blueprint
    from app.api import api
    app.register_blueprint(api, url_prefix='/api')

    return app
