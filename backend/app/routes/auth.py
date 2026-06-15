from flask import request, Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.model.customer import Customer
from app.model.admin import Admin
from werkzeug.security import check_password_hash

auth = Blueprint("auth", __name__, url_prefix="/")

@auth.route("/register", methods=["GET", "POST"])
def register():
    errors = {}
    
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        age = request.form.get("age")
        gender = request.form.get("gender")
        country = request.form.get("country")
    
        if Customer.query.filter_by(email=email).first():
            errors["email"] = "Email is already registered"
        if len(password) < 6:
            errors["password"] = "The minimum password length is 6 characters"
        elif password != confirm_password:
            errors["confirm_password"] = "Password and confirm password do not match"
            
        if errors:
            return render_template("auth/register.html", errors=errors)
            
        try:
            new_customer = Customer(name=name, email=email, age=age, gender=gender, country=country)
            new_customer.setPassword(password)
            db.session.add(new_customer)
            db.session.commit()
            flash("Registration has been successful", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Registration failed")
    
    return render_template("auth/register.html", errors={})

@auth.route('/login', methods=['GET', 'POST'])
def login():
    errors = {}

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if not email:
            errors['email'] = "Email is required"
        if not password:
            errors['password'] = "Password is required"

        if not errors:
            user = Customer.query.filter_by(email=email).first()
            print(f"[DEBUG] login attempt email={email} found_user={bool(user)}")

            if user and user.checkPassword(password):
                print(f"[DEBUG] password check for {email}: OK")
                # Login berhasil
                session['user_id'] = user.id
                session['user_name'] = user.name

                # Tentukan role berdasarkan tabel admin (DB final)
                admin = Admin.query.filter_by(email=email).first()
                print(f"[DEBUG] admin record found={bool(admin)}")
                if admin and check_password_hash(admin.password, password):
                    print(f"[DEBUG] admin password check for {email}: OK")
                    session['user_role'] = 'admin'
                    flash('Welcome back (admin)!', 'success')
                    return redirect(url_for('admin_rt.dashboard'))

                # default customer
                session['user_role'] = 'customer'
                flash('Welcome back!', 'success')
                return redirect(url_for('customer_rt.dashboard'))

            else:
                errors['password'] = 'Bad email or password'

        # Jika ada error, kembali ke form login
        return render_template('auth/login.html', errors=errors)

    # GET request
    return render_template('auth/login.html', errors={})

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logout was successful', 'success')
    return redirect(url_for('auth.login'))