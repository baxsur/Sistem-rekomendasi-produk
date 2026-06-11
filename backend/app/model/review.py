from app import db
from datetime import datetime


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    review_text = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)
    helpful_votes = db.Column(db.Integer, default=0)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)