import csv
import sys
import time
from app import app, db
from app.model.customer import Customer
from werkzeug.security import generate_password_hash


def extract_email_and_plain(row):
    data = {k.lower(): v for k, v in row.items()}
    e = data.get('email') or data.get('e-mail') or data.get('e_mail')
    if not e:
        for v in row.values():
            if isinstance(v, str) and '@' in v:
                e = v
                break
    if not e:
        return None, None
    # find password key
    for key in ('password', 'passwd', 'pw'):
        if key in data and data.get(key):
            return e.strip().lower(), data.get(key)
    # fallback: last column
    vals = list(row.values())
    if vals:
        return e.strip().lower(), vals[-1]
    return e.strip().lower(), None


def update_all(csv_path):
    total = 0
    updated = 0
    skipped = 0
    errors = 0
    with open(csv_path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        entries = [extract_email_and_plain(r) for r in reader]
    with app.app_context():
        for idx, (email, plain) in enumerate(entries, start=1):
            total += 1
            if not email or not plain:
                skipped += 1
                print(f"{idx}/{len(entries)} SKIP missing data")
                continue
            try:
                user = Customer.query.filter_by(email=email.strip().lower()).first()
                if not user:
                    skipped += 1
                    print(f"{idx}/{len(entries)} NOT_FOUND {email}")
                    continue
                user.password = generate_password_hash(plain, method='pbkdf2:sha256')
                db.session.add(user)
                db.session.commit()
                updated += 1
                print(f"{idx}/{len(entries)} UPDATED {email}")
            except Exception as e:
                db.session.rollback()
                errors += 1
                print(f"{idx}/{len(entries)} ERROR {email}: {e}")
            # small pause to reduce runaway CPU spikes
            time.sleep(0.05)

    print('SUMMARY total=%d updated=%d skipped=%d errors=%d' % (total, updated, skipped, errors))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: update_all_from_csv.py <csv_path>')
        sys.exit(1)
    csv_path = sys.argv[1]
    update_all(csv_path)
