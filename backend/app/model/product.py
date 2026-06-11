from app import db
from datetime import datetime


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    external_id = db.Column(db.String(50), index=True, unique=True, nullable=True)
    product_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120))
    brand = db.Column(db.String(120))
    price = db.Column(db.Float, nullable=False, default=0.0)
    avg_rating = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    discount_pct = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)