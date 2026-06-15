import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Read environment variables with sensible defaults to avoid 'None' host
    HOST = os.environ.get("DB_HOST", "localhost")
    DATABASE = os.environ.get("DB_DATABASE", "aplikasi_data_scientis")
    USERNAME = os.environ.get("DB_USERNAME", "root")
    PASSWORD = os.environ.get("DB_PASSWORD", "")

    if PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}@{HOST}/{DATABASE}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True