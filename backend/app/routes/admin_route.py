from app import db
from flask import request, render_template, session, flash, redirect, url_for, Blueprint
from sqlalchemy import or_, func

from app.model.admin import Admin
from app.model.product import Product
from app.model.customer import Customer
from app.model.transaction import Transaction
from app.model.review import Review
from datetime import datetime, timedelta

admin_rt = Blueprint("admin_rt", __name__, url_prefix='/')

@admin_rt.route("/admin/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    total_sales = db.session.query(func.sum(Transaction.total_amount)).filter_by(status='completed').scalar() or 0.0
    total_orders = Transaction.query.count()
    completed_orders = Transaction.query.filter_by(status='completed').count()
    total_products = Product.query.count()
    
    recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                           active_page='dashboard',
                           total_sales=total_sales,
                           total_orders=total_orders,
                           completed_orders=completed_orders,
                           total_products=total_products,
                           recent_transactions=recent_transactions)
    
@admin_rt.route('/admin/products', methods=['GET', 'POST'])
def products():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category', '')
        brand = request.form.get('brand', '')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity', 0)
        discount_pct = request.form.get('discount_pct', 0.0)

        if not product_name or not price:
            flash('Name and price must be filled in!', 'danger')
        else:
            try:
                new_product = Product(
                    product_name=product_name, 
                    category=category,
                    brand=brand,
                    price=float(price), 
                    stock_quantity=int(stock_quantity), 
                    discount_pct=float(discount_pct)
                )
                db.session.add(new_product)
                db.session.flush()
                new_product.external_id = f"P{new_product.id - 1:04d}"
                db.session.commit()
                flash('Product added successfully!', 'success')
            except Exception:
                db.session.rollback()
                flash('Failed to add product.', 'danger')
                
        return redirect(url_for('admin_rt.products'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '', type=str).strip()
    per_page = 20

    query = Product.query

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.product_name.ilike(like_pattern),
                Product.category.ilike(like_pattern),
                Product.brand.ilike(like_pattern),
                Product.external_id.ilike(like_pattern)
            )
        )

    pagination = query.order_by(Product.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'admin/products.html',
        active_page='products',
        products=pagination.items,
        pagination=pagination,
        search=search
    )


@admin_rt.route('/admin/products/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)
    
    product.product_name = request.form.get('product_name') or product.product_name
    product.category = request.form.get('category') or product.category
    product.brand = request.form.get('brand') or product.brand
    
    try:
        if request.form.get('price'): 
            product.price = float(request.form.get('price'))
        if request.form.get('stock_quantity'): 
            product.stock_quantity = int(request.form.get('stock_quantity'))
        if request.form.get('discount_pct'): 
            product.discount_pct = float(request.form.get('discount_pct'))
            
        db.session.commit()
        flash('Product updated successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to update product. Make sure the number format is correct.', 'danger')
        
    return redirect(url_for('admin_rt.products'))


@admin_rt.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('The product was successfully deleted!', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to delete product. Product may still be tied to order or review data..', 'danger')
        
    return redirect(url_for('admin_rt.products'))

@admin_rt.route('/admin/stock', methods=['GET', 'POST'])
def stock():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        new_stock = request.form.get('stock_quantity')
        
        product = Product.query.get(product_id)
        if product and new_stock is not None:
            try:
                product.stock_quantity = int(new_stock)
                db.session.commit()
                flash(f'Stock for {product.product_name} updated sucessfully!', 'success')
            except Exception:
                db.session.rollback()
                flash('Failed to update stock.', 'danger')
        return redirect(url_for('admin_rt.stock'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '', type=str).strip()
    per_page = 20

    query = Product.query

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.product_name.ilike(like_pattern),
                Product.category.ilike(like_pattern),
                Product.brand.ilike(like_pattern),
                Product.external_id.ilike(like_pattern)
            )
        )

    pagination = query.order_by(Product.stock_quantity.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'admin/stock.html',
        active_page='stock',
        products=pagination.items,
        pagination=pagination,
        search=search
    )
    

@admin_rt.route('/admin/orders', methods=['GET', 'POST'])
def orders():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        new_status = request.form.get('status')

        tx = Transaction.query.get(transaction_id)

        if tx:
            try:
                tx.status = new_status
                db.session.commit()
                flash(f'Order #{tx.id} status updated successfully.', 'success')
            except Exception:
                db.session.rollback()
                flash('Failed to update order status.', 'danger')

        return redirect(request.referrer or url_for('admin_rt.orders'))

    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '')
    date_filter = request.args.get('date_filter', '')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    query = db.session.query(
        Transaction, Customer, Product).join(
        Customer, Transaction.customer_id == Customer.id).join(
        Product, Transaction.product_id == Product.id)

    if keyword:
        query = query.filter(db.or_(Customer.name.ilike(f"%{keyword}%"), 
                                    Product.product_name.ilike(f"%{keyword}%")))

    if status:
        query = query.filter(Transaction.status == status)

    now = datetime.now()

    if date_filter == 'today':
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)
        query = query.filter(Transaction.transaction_date >= start, Transaction.transaction_date < end)
    elif date_filter == 'this_week':
        start = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
        end = start + timedelta(days=7)
        query = query.filter(Transaction.transaction_date >= start, Transaction.transaction_date < end)
    elif date_filter == 'year' and year:
        query = query.filter(db.extract('year', Transaction.transaction_date) == year)
    elif date_filter == 'month' and year and month:
        query = query.filter(
            db.extract('year', Transaction.transaction_date) == year,
            db.extract('month', Transaction.transaction_date) == month
        )

    pagination = query.order_by(Transaction.transaction_date.desc()).paginate(page=page, per_page=20, error_out=False)

    orders_data = []

    for transaction, customer, product in pagination.items:
        orders_data.append({
            'transaction': transaction,
            'customer': customer,
            'product': product
        })

    available_statuses = [s[0] for s in db.session.query(Transaction.status).distinct().all() if s[0]]

    available_years = [y[0] for y in db.session.query(
        db.extract('year', Transaction.transaction_date)
    ).distinct().order_by(db.extract('year', Transaction.transaction_date).desc()).all() if y[0]]
    available_years = [int(y) for y in available_years]

    return render_template(
        'admin/orders.html',
        active_page='orders',
        orders=orders_data,
        pagination=pagination,
        keyword=keyword,
        selected_status=status,
        available_statuses=available_statuses,
        date_filter=date_filter,
        selected_year=year,
        selected_month=month,
        available_years=available_years
    )

@admin_rt.route('/admin/reviews')
def reviews():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    page = request.args.get('page', 1, type=int)
    rating_filter = request.args.get('rating', type=int)
    keyword = request.args.get('keyword', '').strip()
    per_page = 21

    query = db.session.query(
        Review, Customer, Product).join(
        Customer, Review.customer_id == Customer.id).join(
        Product, Review.product_id == Product.id)

    if rating_filter:
        query = query.filter(Review.rating == rating_filter)

    if keyword:
        query = query.filter(db.or_(
            Customer.name.ilike(f"%{keyword}%"),
            Product.product_name.ilike(f"%{keyword}%")
        ))

    pagination = query.order_by(Review.review_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    reviews_data = []
    for r, customer, product in pagination.items:
        reviews_data.append({
            'review': r,
            'customer': customer,
            'product': product
        })

    avg_rating = db.session.query(db.func.avg(Review.rating)).scalar()
    total_reviews = db.session.query(db.func.count(Review.id)).scalar()

    return render_template(
        'admin/reviews.html',
        active_page='reviews',
        reviews=reviews_data,
        pagination=pagination,
        rating_filter=rating_filter,
        keyword=keyword,
        avg_rating=round(avg_rating, 1) if avg_rating else 0,
        total_reviews=total_reviews
    )


@admin_rt.route('/admin/profile', methods=['GET', 'POST'])
def profile():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    admin = Admin.query.get(session["admin_id"])

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not name or not email:
            flash('Name and email must be filled in!', 'danger')
            return redirect(url_for('admin_rt.profile'))

        existing = Admin.query.filter(Admin.email == email, Admin.id != admin.id).first()
        if existing:
            flash('Email is already used by another account.', 'danger')
            return redirect(url_for('admin_rt.profile'))

        try:
            admin.name = name
            admin.email = email

            if new_password:
                if new_password != confirm_password:
                    flash('Password confirmation does not match.', 'danger')
                    return redirect(url_for('admin_rt.profile'))
                admin.setPassword(new_password)

            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception:
            db.session.rollback()
            flash('Failed to update profile.', 'danger')

        return redirect(url_for('admin_rt.profile'))

    return render_template('admin/profile.html', active_page='profile', admin=admin)