from flask import request, Blueprint, redirect, session, url_for, flash, render_template
from sqlalchemy import func
from app import app, db
from app.model.customer import Customer
from app.model.transaction import Transaction
from app.model.product import Product
from app.model.review import Review

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


@customer_rt.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = Customer.query.get(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.logout'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        country = request.form.get('country')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password:
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return render_template('customer/profile.html', user=user)
            if password != confirm_password:
                flash('Password confirmation does not match', 'danger')
                return render_template('customer/profile.html', user=user)
            user.setPassword(password)

        # update basic fields
        user.name = name or user.name
        try:
            user.age = int(age) if age else user.age
        except Exception:
            pass
        user.gender = gender or user.gender
        user.country = country or user.country

        try:
            db.session.commit()
            flash('Profile updated', 'success')
            session['user_name'] = user.name
            return redirect(url_for('customer_rt.profile'))
        except Exception:
            db.session.rollback()
            flash('Failed to update profile', 'danger')

    return render_template('customer/profile.html', user=user)


@customer_rt.route('/orders', methods=['GET'])
def orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    txs = Transaction.query.filter_by(customer_id=user_id).order_by(Transaction.transaction_date.desc()).all()

    # attach product info for each transaction
    orders = []
    for t in txs:
        product = Product.query.get(t.product_id)
        orders.append({'transaction': t, 'product': product})

    return render_template('customer/orders.html', orders=orders)


@customer_rt.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
def review_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)

    # Ensure user purchased and transaction completed
    purchase = Transaction.query.filter_by(customer_id=user_id, product_id=product_id, status='completed').first()
    if not purchase:
        flash('You can only review products you have completed transactions for', 'warning')
        return redirect(url_for('customer_rt.orders'))

    existing = Review.query.filter_by(customer_id=user_id, product_id=product_id).first()

    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        review_text = request.form.get('review_text', '').strip()

        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5', 'danger')
            return render_template('customer/review.html', product=product, existing=existing)

        try:
            if existing:
                existing.rating = rating
                existing.review_text = review_text
                existing.review_date = func.now()
            else:
                new_rev = Review(customer_id=user_id, product_id=product_id, rating=rating, review_text=review_text)
                db.session.add(new_rev)

            db.session.commit()

            # recompute aggregate rating for product
            avg = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar() or 0.0
            cnt = db.session.query(func.count(Review.id)).filter(Review.product_id == product_id).scalar() or 0
            product.avg_rating = float(avg)
            product.num_ratings = int(cnt)
            db.session.commit()

            flash('Thanks for your review', 'success')
            return redirect(url_for('customer_rt.orders'))
        except Exception:
            db.session.rollback()
            flash('Failed to save review', 'danger')

    return render_template('customer/review.html', product=product, existing=existing)