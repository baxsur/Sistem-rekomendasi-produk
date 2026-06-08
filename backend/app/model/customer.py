from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(230), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(180), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    signup_date = db.Column(db.Date, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def setPassword(self, password):
        self.password = generate_password_hash(password)
        
    def checkPassword(self, password):
        return check_password_hash(self.password, password)
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "age": self.age,
            "gender": self.gender,
            "country": self.country,
            "singup_date": self.signup_date,
            "updated_at": self.updated_at
        }
    
    
    