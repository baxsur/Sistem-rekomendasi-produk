import csv
import sys
from app import app, db
from app.model.customer import Customer
from werkzeug.security import generate_password_hash

CSV_PATH_DEFAULT = '..\\customers.csv'

def update_passwords(csv_path=CSV_PATH_DEFAULT):
    updated = 0
    missing = 0
    with app.app_context():
        with open(csv_path, newline='', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # find email and plain password in common columns
                email = None
                plain = None
                for k, v in row.items():
                    kl = k.lower()
                    if kl in ('email','e-mail','e_mail','user_email','email_address') and v:
                        email = v.strip().lower()
                    if kl in ('password','passwd','pw') and v is not None:
                        plain = v
                if not email:
                    # fallback: any value that contains @
                    for v in row.values():
                        if isinstance(v, str) and '@' in v:
                            email = v.strip().lower()
                            break
                if email is None or plain is None:
                    continue
                user = Customer.query.filter_by(email=email).first()
                if user:
                    # use pbkdf2:sha256 for speed/reproducibility
                    user.password = generate_password_hash(plain, method='pbkdf2:sha256')
                    db.session.add(user)
                    updated += 1
                else:
                    missing += 1
        db.session.commit()
    print(f'Updated: {updated}, missing (no user): {missing}')

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH_DEFAULT
    update_passwords(path)
