import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .db import db_init

def create_app(test_config=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('PFMS_SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///data.db'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret'),
    )
    CORS(app)
    jwt = JWTManager(app)
    db_init(app)

    # Register blueprints
    from .auth import auth_bp
    from .transactions import tx_bp
    from .ml_routes import model_bp
    from .consent import consent_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tx_bp, url_prefix='/api/transactions')
    app.register_blueprint(model_bp, url_prefix='/api/models')
    app.register_blueprint(consent_bp, url_prefix='/api')
    from .aggregator import agg_bp
    app.register_blueprint(agg_bp, url_prefix='/api/aggregator')

    # Simple dashboard
    from flask import render_template

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
