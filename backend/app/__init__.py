from flask import Flask, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "kunci rahasia"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.model import customer, product, review, transaction, admin
from app.routes.auth import auth
from app.routes.customer_route import customer_rt
from app.routes.admin_route import admin_rt

app.register_blueprint(auth)
app.register_blueprint(customer_rt)
app.register_blueprint(admin_rt)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

# from app.seeders.import_data import import_customers
# from app.seeders.import_data import import_products
# from app.seeders.import_data import import_transactions
# from app.model.product import Product

# with app.app_context():
#     if Product.query.count() == 0:
#         import_customers()
#         import_products()
#         import_transactions()
    