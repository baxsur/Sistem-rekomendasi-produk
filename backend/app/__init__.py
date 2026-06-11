from flask import Flask, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "kunci rahasia"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.model import customer, product, review, transaction
from app.routes.auth import auth
from app.routes.customer_route import customer_rt
from app.routes.admin_route import admin_rt

app.register_blueprint(auth)
app.register_blueprint(customer_rt)
app.register_blueprint(admin_rt)

for rule in app.url_map.iter_rules():
    print(rule)