import csv
import sys
from app import app, db
from app.model.customer import Customer
from werkzeug.security import generate_password_hash

def find_plain(csv_path, email):
    with open(csv_path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize keys
            data = {k.lower(): v for k, v in row.items()}
            e = data.get('email') or data.get('e-mail') or data.get('e_mail')
            if not e:
                for v in row.values():
                    if isinstance(v, str) and email.split('@')[0] in v:
                        e = v
                        break
            if e and e.strip().lower() == email.strip().lower():
                # find password key
                for key in ('password','passwd','pw'):
                    if key in data:
                        return data.get(key)
                # fallback: try last column
                vals = list(row.values())
                if vals:
                    return vals[-1]
    return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: update_single_from_csv.py <csv_path> <email>')
        sys.exit(1)
    csv_path = sys.argv[1]
    email = sys.argv[2]
    plain = find_plain(csv_path, email)
    if not plain:
        print('PLAIN_NOT_FOUND')
        sys.exit(1)
    with app.app_context():
        user = Customer.query.filter_by(email=email.strip().lower()).first()
        if not user:
            print('USER_NOT_FOUND')
            sys.exit(1)
        user.password = generate_password_hash(plain, method='pbkdf2:sha256')
        db.session.add(user)
        db.session.commit()
        # refresh from db
        user = Customer.query.filter_by(email=email.strip().lower()).first()
        print('UPDATED', email)
        print('VERIFY', user.checkPassword(plain))