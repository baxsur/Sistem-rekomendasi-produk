from app import create_app
from app.recommender import build_and_save

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        ok = build_and_save()

        if ok:
            print('Recommender built')
        else:
            print('No data to build recommender')

