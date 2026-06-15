import csv
from app import app
from app.model.customer import Customer

SAMPLES = [
    'user_c00000@gmail.com',
    'user_c02500@gmail.com',
    'user_c04749@gmail.com'
]


def find_plain(csv_path, email):
    with open(csv_path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = {k.lower(): v for k, v in row.items()}
            e = data.get('email') or data.get('e-mail') or data.get('e_mail')
            if e and e.strip().lower() == email.strip().lower():
                for key in ('password', 'passwd', 'pw'):
                    if key in data and data.get(key):
                        return data.get(key)
                vals = list(row.values())
                if vals:
                    return vals[-1]
    return None


def verify(csv_path):
    with app.app_context():
        for email in SAMPLES:
            user = Customer.query.filter_by(email=email.strip().lower()).first()
            plain = find_plain(csv_path, email)
            print('---', email)
            print('user_found:', bool(user))
            print('plain_from_csv:', bool(plain))
            if user:
                try:
                    ok = user.checkPassword(plain) if plain else False
                except Exception as e:
                    ok = False
                print('checkPassword with CSV plain:', ok)
            print()


if __name__ == '__main__':
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else '..\\customers.csv'
    verify(csv_path)
