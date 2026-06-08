from flask import Flask, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.secret_key = "kunci rahasia"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.model import customer
from app.routes.auth import auth

app.register_blueprint(auth)