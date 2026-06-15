from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def setPassword(self, password):
        self.password = generate_password_hash(password)
        
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Admin {self.email}>"
