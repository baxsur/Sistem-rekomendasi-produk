from flask import Flask, session
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
    from app.model.admin import Admin

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
    
    @app.context_processor
    def inject_current_admin():
        if "admin_id" in session:
            admin = Admin.query.get(session["admin_id"])
            return {"current_admin": admin}
        return {"current_admin": None}
    
    with app.app_context():
        if Admin.query.count() == 0:
            new_admin = Admin(email="admin@email.com", name="admin")
            new_admin.setPassword("123456")
            db.session.add(new_admin)
            db.session.commit()

    return app




