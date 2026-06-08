from flask import request, jsonify, Blueprint
from app import db
from app.model.customer import Customer

auth = Blueprint("auth", __name__, url_prefix="/")

@auth.route("/customer", methods=["GET"])
def get_customer():
    customer = Customer.query.all()
    json_customer = list(map(lambda x: x.to_json(), customer))
    return jsonify({"Customer": json_customer})

@auth.route("/create_customer", methods=["GET", "POST"])
def create_customer():
    name = request.json.get("name")
    email = request.json.get("email")
    password = request.json.get("password")
    confirm_password = request.json.get("confirm_password")
    age = request.json.get("age")
    gender = request.json.get("gender")
    country = request.json.get("country")
    
    if not name:
        return (jsonify({"message": "Name cannot be empty"}), 400)
    elif not email:
        return (jsonify({"message": "Email cannot be empty"}), 400)
    elif Customer.query.filter_by(email=email).first():
        return (jsonify({"message": "Email is already registered"}), 400)
    elif not password:
        return (jsonify({"message": "Password cannot be empty"}), 400)
    elif len(password) < 6:
        return (jsonify({"message": "The minimum password length is 6 characters"}), 400)
    elif not confirm_password:
        return (jsonify({"message": "Confirm Password cannot be empty"}), 400)
    elif password != confirm_password:
        return (jsonify({"message": "Password and confirm password do not match"}), 400)
    elif not age:
        return (jsonify({"message": "Age cannot be empty"}), 400)
    elif not gender:
        return (jsonify({"message": "Gender cannot be empty"}), 400)
    elif not country:
        return (jsonify({"message": "Country cannot be empty"}), 400)
        
        
    try:
        new_customer = Customer(name=name, email=email, age=age, gender=gender, country=country)
        new_customer.setPassword(password)
        db.session.add(new_customer)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message": "User created!"}), 200