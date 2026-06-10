import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    HOST = str(os.environ.get("DB_HOST"))
    DATABASE = str(os.environ.get("DB_DATABASE"))
    USERNAME = str(os.environ.get("DB_USERNAME"))
    PASSWORD = str(os.environ.get("DB_PASSWORD"))
    
    # JWT CONFIG
    JWT_SECRET_KEY = str(os.environ.get("JWT_SECRET"))
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=int(os.environ.get("JWT_TOKEN_EXPIRES", 24)))
    
    # Cookie settings
    JWT_TOKEN_LOCATION = os.environ.get("JWT_LOCATION", "headers").split(",")
    JWT_COOKIE_SECURE = os.environ.get("JWT_SECURE", "False").lower() == "true"
    JWT_COOKIE_HTTPONLY = os.environ.get("JWT_HTTP", "True").lower() == "true"
    JWT_COOKIE_SAMESITE = str(os.environ.get("JWT_SAMESITE"))
    JWT_COOKIE_CSRF_PROTECT = str(os.environ.get("JWT_CSRF", "True")).lower() == "true"
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + USERNAME + ':' + PASSWORD + '@' + HOST + '/' + DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True