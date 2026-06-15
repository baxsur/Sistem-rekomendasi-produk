from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import logging

# buat instance db/migrate di module scope (tidak di-bind ke app)
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class or Config)
    app.secret_key = "kunci rahasia"

    # inisialisasi ekstensi dengan app
    db.init_app(app)
    migrate.init_app(app, db)

    # import model dan blueprint setelah db terinisialisasi untuk hindari circular import
    from app.model import customer, product, review, transaction  # pastikan model mengimpor db dari app: from app import db
    from app.routes.auth import auth
    from app.routes.customer_route import customer_rt
    from app.routes.admin_route import admin_rt

    # register blueprint
    app.register_blueprint(auth)
    app.register_blueprint(customer_rt)
    app.register_blueprint(admin_rt)

    try:
        from .api import api as api_bp
        app.register_blueprint(api_bp)
    except Exception as e:
        logging.getLogger(__name__).warning("Could not register API blueprint: %s", e)

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}

    return app

# NOTE: do NOT create `app = create_app()` here to avoid circular import.
# Use run.py (or set FLASK_APP=run:app) to start the server.