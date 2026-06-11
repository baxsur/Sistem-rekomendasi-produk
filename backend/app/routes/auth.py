from flask import request, jsonify, Blueprint
from app import db
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies, unset_refresh_cookies)
from app.model.customer import Customer

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth.route("/register", methods=["GET", "POST"])
def register():
    name = request.json.get("name")
    email = request.json.get("email")
    password = request.json.get("password")
    confirm_password = request.json.get("confirm_password")
    age = request.json.get("age")
    gender = request.json.get("gender")
    country = request.json.get("country")
    
    if Customer.query.filter_by(email=email).first():
        return (jsonify({"message": "Email is already registered"}), 400)
    elif len(password) < 6:
        return (jsonify({"message": "The minimum password length is 6 characters"}), 400)
    elif password != confirm_password:
        return (jsonify({"message": "Password and confirm password do not match"}), 400)
        
    try:
        new_customer = Customer(name=name, email=email, age=age, gender=gender, country=country)
        new_customer.setPassword(password)
        db.session.add(new_customer)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message": "User created!"}), 200

@auth.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")
    
    user = Customer.query.filter_by(email=email).first()
    
    if user and user.checkPassword(password):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role})
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={"role": user.role})
        
        resp = jsonify({"message": "Login successful"})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    
    return jsonify({"message": "Bad username or password"}), 400

# untuk cek siapa yang login
@auth.route("/me", methods=["GET"])
@jwt_required()
def me():

    user_id = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "id": user_id,
        "role": claims["role"]
    }), 200

@auth.route("/logout", methods=["POST"])
# @jwt_required()   
def logout():
    resp = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(resp)   
    return resp, 200