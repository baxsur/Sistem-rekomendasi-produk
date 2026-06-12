from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    external_id = db.Column(db.String(50), index=True, unique=True, nullable=True)
    name = db.Column(db.String(230), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(180), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    
    signup_date = db.Column(db.Date, default=datetime.utcnow)
    # Relationships
    reviews = db.relationship('Review', backref='customer', lazy='dynamic', cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='customer', lazy='dynamic', cascade="all, delete-orphan")
    
    def setPassword(self, password):
        self.password = generate_password_hash(password)
        
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'country': self.country,
            'signup_date': None if not self.signup_date else self.signup_date.isoformat(),
            'role': self.role,
        }
    
    
    