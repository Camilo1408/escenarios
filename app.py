from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///local.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from db.models import db

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from blueprints.dashboard import bp as dashboard_bp
    from blueprints.escenarios import bp as escenarios_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(escenarios_bp, url_prefix='/escenarios')

    return app

app = create_app()