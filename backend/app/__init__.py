from flask import Flask, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

app = Flask(__name__)
CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173",
              "http://127.0.0.1:5173"])
app.config.from_object(Config)
app.secret_key = "kunci rahasia"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

from app.model import customer
from app.routes.auth import auth

app.register_blueprint(auth)