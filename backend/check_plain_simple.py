import csv
import sys
from app import create_app
from app.model.customer import Customer

CSV_DEFAULT = '..\\customers.csv'

def find_plain_password(csv_path, email):
    with open(csv_path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # try common column names
            e = None
            for key in row.keys():
                if key.lower() in ('email','e-mail','e_mail','user_email','email_address'):
                    e = row.get(key)
                    break
            if not e:
                # fallback: find any field that looks like email
                for v in row.values():
                    if isinstance(v, str) and '@' in v:
                        e = v
                        break
            pwd = None
            for key in row.keys():
                if key.lower() in ('password','passwd','pw'):
                    pwd = row.get(key)
                    break
            if e and e.strip().lower() == email.strip().lower():
                return pwd
    return None

app = create_app()

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    email = sys.argv[2] if len(sys.argv) > 2 else 'user_c00000@gmail.com'
    try:
        plain = find_plain_password(csv_path, email)
    except FileNotFoundError:
        print('CSV_NOT_FOUND')
        sys.exit(1)
    if not plain:
        print('PLAIN_NOT_FOUND')
    else:
        print('PLAIN_FOUND')
    with app.app_context():
        user = Customer.query.filter_by(email=email.strip().lower()).first()
        if not user:
            print('USER_NOT_IN_DB')
            sys.exit(0)
        if plain:
            try:
                ok = user.checkPassword(plain)
                print('CHECK_PLAIN_MATCH', ok)
            except Exception as e:
                print('CHECK_ERROR', e)
        else:
            print('NO_PLAIN_TO_CHECK')
