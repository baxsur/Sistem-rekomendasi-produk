import pandas as pd
from datetime import datetime

from app import app, db
from app.model.customer import Customer
from app.model.product import Product
from app.model.transaction import Transaction

CUSTOMERS_CSV = "app/seeders/customers_login.csv"
PRODUCTS_CSV = "app/seeders/products.csv"
TRANSACTIONS_CSV = "app/seeders/transactions.csv"


def import_customers():
    df = pd.read_csv(CUSTOMERS_CSV)

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        email = str(row["email"]).strip().lower()

        if Customer.query.filter_by(email=email).first():
            continue

        customer = Customer(
            external_id=row["customer_id"],
            name=row['username'],
            email=row["email"],
            age=int(row["age"]),
            gender=row["gender"],
            country=row["country"]
        )

        customer.setPassword(str(row["password"]))

        db.session.add(customer)
        if i % 1000 == 0:
            print(f"{i} customers processed")

    db.session.commit()

    print("Customers imported")


def import_products():
    df = pd.read_csv(PRODUCTS_CSV)

    for _, row in df.iterrows():

        if Product.query.filter_by(
            external_id=row["product_id"]
        ).first():
            continue

        product = Product(
            external_id=row["product_id"],
            product_name=row["product_name"],
            category=row["category"],
            brand=row["brand"],
            price=float(row["price"]),
            avg_rating=float(row["avg_rating"]),
            num_ratings=int(row["num_ratings"]),
            stock_quantity=int(row["stock_quantity"]),
            discount_pct=float(row["discount_pct"])
        )

        db.session.add(product)

    db.session.commit()

    print("Products imported")


def import_transactions():
    df = pd.read_csv(TRANSACTIONS_CSV)

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        customer = Customer.query.filter_by(
            external_id=row["customer_id"]
        ).first()

        product = Product.query.filter_by(
            external_id=row["product_id"]
        ).first()

        if not customer or not product:
            continue

        transaction = Transaction(
            transaction_date=datetime.strptime(
                row["transaction_date"],
                "%Y-%m-%d %H:%M:%S"
            ),
            customer_id=customer.id,
            product_id=product.id,
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
            total_amount=float(row["total_amount"]),
            discount=float(row["discount_applied"]),
            payment_method=row["payment_method"],
            shipping_cost=float(row["shipping_cost"]),
            status=row["status"]
        )

        db.session.add(transaction)
        if i % 1000 == 0:
            print(f"{i} transactions processed")

    db.session.commit()

    print("Transactions imported")


if __name__ == "__main__":
    with app.app_context():

        print("Importing customers...")
        import_customers()

        print("Importing products...")
        import_products()

        print("Importing transactions...")
        import_transactions()

        print("Done.")