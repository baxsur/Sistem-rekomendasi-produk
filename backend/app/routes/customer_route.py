from flask import request, Blueprint, redirect, session, url_for, flash, render_template
from app import app, db
from app.model.customer import Customer

customer_rt = Blueprint("customer_rt", __name__, url_prefix="/")

@customer_rt.route('/')
def index():
    # Jika user sudah login, redirect ke halaman sesuai role
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin_rt.dashboard'))
        else:
            return redirect(url_for('customer_rt.dashboard'))
    
    # Jika belum login, tampilkan landing page
    return render_template('index.html')

@customer_rt.route("/dashboard", methods=["GET"])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('customer/dashboard.html')