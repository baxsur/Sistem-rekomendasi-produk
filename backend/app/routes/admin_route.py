from app import app, db
from flask import request, render_template, session, flash, redirect, url_for, Blueprint
from app.model.product import Product

admin_rt = Blueprint("admin_rt", __name__, url_prefix='/')

@admin_rt.route("/admin/dashboard")
def dashboard():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    products = Product.query.order_by(Product.id.desc()).all()

    return render_template("admin/dashboard.html", products=products)
    
@admin_rt.route("/product/<int:product_id>")
def product_detail(product_id):

    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)

    return render_template("admin/product_detail.html", product=product)

@admin_rt.route("/product/add", methods=["GET", "POST"])
def add_product():

    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Access denied.', 'danger')
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

    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Access denied.', 'danger')
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

    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Access denied.', 'danger')
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