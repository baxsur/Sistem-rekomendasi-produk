from app import app, db
from flask import request, render_template, session, flash, redirect, url_for, Blueprint
from app.model.product import Product
from app.model.admin import Admin
from sqlalchemy import or_

admin_rt = Blueprint("admin_rt", __name__, url_prefix='/')

@admin_rt.route("/admin/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query

    if keyword:
        query = query.filter(
            or_(
                Product.product_name.ilike(f"%{keyword}%"),
                Product.external_id.ilike(f"%{keyword}%"),
                Product.brand.ilike(f"%{keyword}%")
            )
        )

    if category:
        query = query.filter(Product.category == category)

    products = query.order_by(Product.id.desc()).all()

    categories = [
        "Health", "Beauty", "Office Supplies", "Electronics",
        "Pet Supplies", "Sports", "Clothing", "Food & Grocery",
        "Jewelry", "Music", "Automotive", "Books",
        "Home & Garden", "Toys", "Software"
    ]
    
    total_products = query.count()
    total_categories = len(categories)
    
    return render_template(
        "admin/dashboard.html",
        products=products,
        categories=categories,
        selected_category=category,
        total_products=total_products,
        total_categories=total_categories
    )
    
@admin_rt.route("/product/<int:product_id>")
def product_detail(product_id):

    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)

    return render_template("admin/product_detail.html", product=product)

@admin_rt.route("/product/add", methods=["GET", "POST"])
def add_product():

    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        try:
            product = Product(
                product_name=request.form.get("product_name"),
                category=request.form.get("category"),
                brand=request.form.get("brand"),
                price=float(request.form.get("price", 0)),
                stock_quantity=int(request.form.get("stock_quantity", 0)),
                discount_pct=float(request.form.get("discount_pct", 0))
            )
            db.session.add(product)
            # supaya ID langsung dibuat
            db.session.flush()
            # generate external_id
            product.external_id = f"P{product.id:04d}"
            db.session.commit()
            flash("Product added successfully.", "success")

            return redirect(url_for("admin_rt.dashboard"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to add product: {str(e)}","danger")

    return render_template("admin/add_product.html")

@admin_rt.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):

    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        try:
            product.product_name = request.form.get("product_name")
            product.category = request.form.get("category")
            product.brand = request.form.get("brand")
            product.price = float(request.form.get("price", 0))
            product.stock_quantity = int(request.form.get("stock_quantity", 0))
            product.discount_pct = float(request.form.get("discount_pct", 0))

            db.session.commit()
            flash("Product updated successfully.", "success")
            return redirect(url_for("admin_rt.product_detail",product_id=product.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update product: {str(e)}", "danger")

    categories = [
        "Health",
        "Beauty",
        "Office Supplies",
        "Electronics",
        "Pet Supplies",
        "Sports",
        "Clothing",
        "Food & Grocery",
        "Jewelry",
        "Music",
        "Automotive",
        "Books",
        "Home & Garden",
        "Toys",
        "Software"
    ]

    return render_template("admin/edit_product.html", product=product, categories=categories)

@admin_rt.route("/product/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):

    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete product: {str(e)}", "danger")

    return redirect(url_for("admin_rt.dashboard"))

# ===========================================================================
# ============================== profile ====================================
# ===========================================================================

@admin_rt.route("/admin/profile", methods=["GET", "POST"])
def profile():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    admin = Admin.query.get_or_404(session["admin_id"])
    
    if request.method == "POST":
        action = request.form.get("action")
        # UPDATE PROFILE
        if action == "update_profile":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            existing_admin = Admin.query.filter(Admin.email == email, Admin.id != admin.id).first()

            if existing_admin:
                flash("Email is already in use.", "danger")
                return redirect(url_for("admin_rt.profile"))

            admin.name = name
            admin.email = email

            db.session.commit()

            session["admin_name"] = name
            flash("Profile updated successfully.", "success")
            return redirect(url_for("admin_rt.profile"))

        # UPDATE PASSWORD
        elif action == "change_password":

            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not admin.password == current_password:
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("admin_rt.profile"))

            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return redirect(url_for("admin_rt.profile"))

            if new_password != confirm_password:
                flash("New password and confirmation do not match.", "danger")
                return redirect(url_for("admin_rt.profile"))
            
            admin.password = new_password
            db.session.commit()
            flash("Password updated successfully.", "success")

            return redirect(url_for("admin_rt.profile"))

    return render_template("admin/profile.html",admin=admin)

from app.model.transaction import Transaction

# ===========================================================================
# ============================ manage orders ================================
# ===========================================================================

@admin_rt.route("/admin/orders")
def manage_orders():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    status = request.args.get("status", "").strip()
    query = Transaction.query

    if status:
        query = query.filter(Transaction.status == status)

    orders = query.order_by(Transaction.transaction_date.desc()).all()

    statuses = ["pending", "processing", "shipped", "completed", "cancelled"]

    return render_template(
        "admin/orders.html",
        orders=orders,
        statuses=statuses,
        selected_status=status
    )
    
@admin_rt.route("/admin/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))

    order = Transaction.query.get_or_404(order_id)
    new_status = request.form.get("status")
    order.status = new_status
    db.session.commit()

    flash("Order status updated successfully.", "success")
    return redirect(url_for("admin_rt.manage_orders"))