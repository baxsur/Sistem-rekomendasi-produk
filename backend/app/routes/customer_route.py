from flask import request, Blueprint, jsonify
from app import app, db
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.model.customer import Customer

customer_rt = Blueprint("customer_rt", __name__, url_prefix="/api/customer")

@customer_rt.route("/dashboard_c", methods=["GET"])
@jwt_required()
def get_customer():
    current_user = get_jwt_identity()   
    customer = Customer.query.get(int(current_user))
    return jsonify({"customer": customer.to_json()}), 200