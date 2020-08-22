import os
from app.pylib import ad_settings

basedir = os.path.abspath(os.path.dirname(__file__)) + "\\app\\"
#print("basedir:\t" + str(basedir))

class Config(object):
    SECRET_KEY = os.urandom(24).hex()
    ENABLE_LOG = 0
    DB_USER = ad_settings.db_user
    DB_PWD = ad_settings.db_pwd
    DB_HOST = ad_settings.db_host
    DB_DB = ad_settings.db_db
    CAR_IMAGES = os.path.join(basedir, 'static\\uploads\\images\\cars')
    CAR_IMG_PATH = 'uploads/images/cars/'
