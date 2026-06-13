from flask import request, render_template, session, flash, redirect, url_for, Blueprint
from sqlalchemy import func
from app import app, db

# Import model yang sudah kamu buat
from app.model.customer import Customer
from app.model.transaction import Transaction
from app.model.product import Product
from app.model.review import Review

admin_rt = Blueprint("admin_rt", __name__, url_prefix='/')

def is_admin():
    return 'user_role' in session and session['user_role'] == 'admin'

@admin_rt.route('/admin/dashboard')
def dashboard():
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))
    
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
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        external_id = request.form.get('external_id', '')
        category = request.form.get('category', '')
        brand = request.form.get('brand', '')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity', 0)
        discount_pct = request.form.get('discount_pct', 0.0)

        if not product_name or not price:
            flash('Nama dan harga produk wajib diisi!', 'danger')
        else:
            try:
                new_product = Product(
                    product_name=product_name, 
                    external_id=external_id,
                    category=category,
                    brand=brand,
                    price=float(price), 
                    stock_quantity=int(stock_quantity), 
                    discount_pct=float(discount_pct)
                )
                db.session.add(new_product)
                db.session.commit()
                flash('Produk berhasil ditambahkan!', 'success')
            except Exception:
                db.session.rollback()
                flash('Gagal menambahkan produk.', 'danger')
                
        return redirect(url_for('admin_rt.products'))

    all_products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin/products.html', active_page='products', products=all_products)


@admin_rt.route('/admin/products/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    
    product.product_name = request.form.get('product_name') or product.product_name
    product.external_id = request.form.get('external_id') or product.external_id
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
        flash('Produk berhasil diperbarui!', 'success')
    except Exception:
        db.session.rollback()
        flash('Gagal memperbarui produk. Pastikan format angka benar.', 'danger')
        
    return redirect(url_for('admin_rt.products'))


@admin_rt.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Produk berhasil dihapus!', 'success')
    except Exception:
        db.session.rollback()
        flash('Gagal menghapus produk. Produk mungkin masih terikat dengan data pesanan atau ulasan.', 'danger')
        
    return redirect(url_for('admin_rt.products'))

@admin_rt.route('/admin/stock', methods=['GET', 'POST'])
def stock():
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        new_stock = request.form.get('stock_quantity')
        
        product = Product.query.get(product_id)
        if product and new_stock is not None:
            try:
                product.stock_quantity = int(new_stock)
                db.session.commit()
                flash(f'Stok untuk {product.product_name} berhasil diperbarui!', 'success')
            except Exception:
                db.session.rollback()
                flash('Gagal memperbarui stok.', 'danger')
        return redirect(url_for('admin_rt.stock'))

    all_products = Product.query.order_by(Product.stock_quantity.asc()).all()
    return render_template('admin/stock.html', active_page='stock', products=all_products)

@admin_rt.route('/admin/orders', methods=['GET', 'POST'])
def orders():
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        new_status = request.form.get('status')
        
        tx = Transaction.query.get(transaction_id)
        if tx:
            try:
                tx.status = new_status
                db.session.commit()
                flash(f'Status pesanan #{tx.id} berhasil diubah menjadi {new_status}!', 'success')
            except Exception:
                db.session.rollback()
                flash('Gagal mengubah status pesanan.', 'danger')
        return redirect(url_for('admin_rt.orders'))

    txs = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    orders_data = []
    for t in txs:
        customer = Customer.query.get(t.customer_id)
        product = Product.query.get(t.product_id)
        orders_data.append({
            'transaction': t,
            'customer': customer,
            'product': product
        })

    return render_template('admin/orders.html', active_page='orders', orders=orders_data)

@admin_rt.route('/admin/reviews')
def reviews():
    # if not is_admin():
    #     flash('Akses ditolak.', 'danger')
    #     return redirect(url_for('auth.login'))

    all_reviews = Review.query.order_by(Review.review_date.desc()).all()
    reviews_data = []
    for r in all_reviews:
        customer = Customer.query.get(r.customer_id)
        product = Product.query.get(r.product_id)
        reviews_data.append({
            'review': r,
            'customer': customer,
            'product': product
        })

    return render_template('admin/reviews.html', active_page='reviews', reviews=reviews_data)

@admin_rt.route('/admin/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Anda telah berhasil keluar.', 'success')
    return redirect(url_for('auth.login'))