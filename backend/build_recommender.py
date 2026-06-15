from app import app
from app.recommender import build_and_save

if __name__ == '__main__':
    with app.app_context():
        ok = build_and_save()

        if ok:
            print('Recommender built')
        else:
            print('No data to build recommender')

