from flask import request, Blueprint, redirect, session, url_for, flash, render_template
from sqlalchemy import func, or_
from app import db
from app.model.customer import Customer
from app.model.transaction import Transaction
from app.model.product import Product
from app.model.review import Review
from app.recommender import recommend_for_customer
from flask import abort
import json
from sqlalchemy import func
from datetime import datetime, timedelta

customer_rt = Blueprint('customer_rt', __name__)

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

    user_id = session['user_id']

    # load recommendations for current user
    try:
        recs = recommend_for_customer(user_id, top_n=8)
    except Exception:
        recs = []

    # show recent activity summary
    try:
        current_orders_count = (
            db.session.query(func.count(Transaction.id))
            .filter(Transaction.customer_id == user_id)
            .scalar()
        )
    except Exception:
        current_orders_count = 0

    return render_template(
        'customer/dashboard.html',
        recommendations=recs,
        current_orders_count=current_orders_count,
    )

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


@customer_rt.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    return render_template('customer/product_detail.html', product=product)


@customer_rt.route('/product/<int:product_id>/chart', methods=['GET'])
def product_chart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)

    # get sales counts for last 14 days
    end = datetime.utcnow()
    start = end - timedelta(days=13)
    q = (
        db.session
        .query(func.date(Transaction.transaction_date).label('d'), func.sum(Transaction.quantity).label('qty'))
        .filter(Transaction.product_id == product_id)
        .filter(Transaction.transaction_date >= start)
        .group_by('d')
        .order_by('d')
    )

    rows = {r.d.strftime('%Y-%m-%d'): int(r.qty) for r in q}

    # build full date range
    labels = []
    data = []
    for i in range(14):
        day = (start + timedelta(days=i)).strftime('%Y-%m-%d')
        labels.append(day)
        data.append(rows.get(day, 0))

    return render_template('customer/product_chart.html', product=product, labels=labels, data=data)


@customer_rt.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
def checkout(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    user_id = session['user_id']

    if request.method == 'POST':
        try:
            qty = int(request.form.get('quantity', 1))
        except Exception:
            qty = 1

        unit_price = float(product.price or 0.0)
        discount = float(product.discount_pct or 0.0)
        total = unit_price * qty * (1 - (discount / 100.0))

        try:
            # create pending transaction(s) and redirect to payment stub
            new_tx = Transaction(customer_id=user_id, product_id=product.id, quantity=qty,
                                 unit_price=unit_price, total_amount=total, discount=discount, status='pending')
            db.session.add(new_tx)
            db.session.commit()

            # store pending tx ids in session for payment confirmation
            pending = session.get('pending_tx_ids', [])
            pending.append(new_tx.id)
            session['pending_tx_ids'] = pending

            flash('Checkout initiated — proceed to payment', 'info')
            return redirect(url_for('customer_rt.cart_pay'))
        except Exception:
            db.session.rollback()
            flash('Failed to start checkout', 'danger')

    return render_template('customer/checkout.html', product=product)

# --- Cart endpoints (session-backed) -------------------------------------------------
@customer_rt.route('/cart/add/<int:product_id>', methods=['GET'])
def cart_add(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        qty = int(request.args.get('qty', 1))
    except Exception:
        qty = 1

    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session['cart'] = cart

    flash('Added to cart', 'success')
    return redirect(url_for('customer_rt.view_cart'))


@customer_rt.route('/cart', methods=['GET'])
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cart = session.get('cart', {})
    items = []
    total = 0.0
    for pid_s, qty in cart.items():
        try:
            pid = int(pid_s)
            p = Product.query.get(pid)
            if not p:
                continue
            subtotal = (p.price or 0.0) * qty * (1 - ((p.discount_pct or 0.0) / 100.0))
            total += subtotal
            items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
        except Exception:
            continue

    return render_template('customer/cart.html', items=items, total=total)


@customer_rt.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Removed from cart', 'info')
    return redirect(url_for('customer_rt.view_cart'))


@customer_rt.route('/cart/checkout', methods=['POST'])
def cart_checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    cart = session.get('cart', {})
    if not cart:
        flash('Cart is empty', 'warning')
        return redirect(url_for('customer_rt.view_cart'))

    user_id = session['user_id']
    created_ids = []
    try:
        for pid_s, qty in cart.items():
            pid = int(pid_s)
            p = Product.query.get(pid)
            if not p:
                continue
            unit_price = float(p.price or 0.0)
            discount = float(p.discount_pct or 0.0)
            total = unit_price * qty * (1 - (discount / 100.0))
            tx = Transaction(customer_id=user_id, product_id=pid, quantity=qty, unit_price=unit_price, total_amount=total, discount=discount, status='pending')
            db.session.add(tx)
            db.session.flush()
            created_ids.append(tx.id)

        db.session.commit()
        # clear cart
        session['cart'] = {}
        # store pending tx ids
        pending = session.get('pending_tx_ids', [])
        pending.extend(created_ids)
        session['pending_tx_ids'] = pending
        flash('Checkout created — proceed to payment', 'info')
        return redirect(url_for('customer_rt.cart_pay'))
    except Exception:
        db.session.rollback()
        flash('Failed to create checkout', 'danger')
        return redirect(url_for('customer_rt.view_cart'))


@customer_rt.route('/cart/pay', methods=['GET', 'POST'])
def cart_pay():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    pending = session.get('pending_tx_ids', [])
    txs = []
    for txid in pending:
        t = Transaction.query.get(txid)
        if t:
            txs.append(t)
    if request.method == 'POST':
        method = request.form.get('payment_method', 'card')
        try:
            for t in txs:
                t.payment_method = method
                t.status = 'completed'
            db.session.commit()
            # clear pending
            session['pending_tx_ids'] = []
            flash('Payment successful — orders updated', 'success')
            return redirect(url_for('customer_rt.orders'))
        except Exception:
            db.session.rollback()
            flash('Payment failed', 'danger')

    return render_template('customer/pay.html', transactions=txs)


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


@customer_rt.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    q = (request.args.get('q') or '').strip()
    category = (request.args.get('category') or '').strip()
    brand = (request.args.get('brand') or '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    in_stock = request.args.get('in_stock')
    sort = request.args.get('sort')

    query = Product.query

    if q:
        pattern = f"%{q}%"
        query = query.filter(or_(Product.product_name.ilike(pattern), Product.brand.ilike(pattern), Product.category.ilike(pattern)))

    if category:
        query = query.filter(Product.category == category)

    if brand:
        query = query.filter(Product.brand == brand)

    try:
        if min_price:
            mp = float(min_price)
            query = query.filter(Product.price >= mp)
    except Exception:
        pass

    try:
        if max_price:
            xp = float(max_price)
            query = query.filter(Product.price <= xp)
    except Exception:
        pass

    if in_stock:
        query = query.filter(Product.stock_quantity > 0)

    # sorting
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.desc())

    results = []
    try:
        results = query.limit(200).all()
    except Exception:
        results = []

    try:
        cats = [r[0] for r in db.session.query(Product.category).filter(Product.category != None).distinct().all()]
    except Exception:
        cats = []
    try:
        brands = [r[0] for r in db.session.query(Product.brand).filter(Product.brand != None).distinct().all()]
    except Exception:
        brands = []

    return render_template('customer/search_results.html', q=q, results=results, categories=cats, brands=brands, selected={
        'category': category,
        'brand': brand,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock': bool(in_stock),
        'sort': sort or ''
    })