from flask import Flask, request, jsonify, session
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
from app.model.admin import Admin
from app.routes.auth import auth
from app.routes.customer_route import customer_rt
from app.routes.admin_route import admin_rt

app.register_blueprint(auth)
app.register_blueprint(customer_rt)
app.register_blueprint(admin_rt)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

@app.context_processor
def inject_current_admin():
    if "admin_id" in session:
        admin = Admin.query.get(session["admin_id"])
        return {"current_admin": admin}
    return {"current_admin": None}

# kalau semisal database masih kosongan

# from app.seeders.import_data import import_customers
# from app.seeders.import_data import import_products
# from app.seeders.import_data import import_transactions
# from app.seeders.import_data import import_reviews
# from app.model.product import Product
# from app.model.customer import Customer
# from app.model.transaction import Transaction 
# from app.model.review import Review

# with app.app_context():
#     if Product.query.count() == 0:
#         import_products()
#     if Review.query.count() == 0:
#         import_reviews()
#     if Customer.query.count() == 0:
#         import_customers()
#     if Transaction.query.count() == 0:
#         import_transactions()

# untuk email dan password bisa diganti di halaman profile admin
with app.app_context():
    if Admin.query.count() == 0:
        new_admin = Admin(email="admin@email.com", name="admin")
        new_admin.setPassword("123456")
        db.session.add(new_admin)
        db.session.commit()
    