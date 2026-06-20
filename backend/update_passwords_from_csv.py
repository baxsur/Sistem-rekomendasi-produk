import csv
from app import app, db
from app.model.customer import Customer
from werkzeug.security import generate_password_hash

CSV_PATH = 'customers_plain.csv'  # Update or pass as arg

def update_passwords(csv_path=CSV_PATH):
    updated = 0
    missing = 0
    with app.app_context():
        with open(csv_path, newline='', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email') or row.get('Email') or row.get('e-mail')
                plain = row.get('password') or row.get('Password') or row.get('passwd')
                if not email or plain is None:
                    continue
                email = email.strip().lower()
                user = Customer.query.filter_by(email=email).first()
                if user:
                    user.password = generate_password_hash(plain)
                    db.session.add(user)
                    updated += 1
                else:
                    missing += 1
        db.session.commit()
    print(f'Updated: {updated}, missing (no user): {missing}')

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    update_passwords(path)
