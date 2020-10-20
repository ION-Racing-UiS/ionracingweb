import os
from app.pylib import ad_settings

basedir = os.path.abspath(os.path.dirname(__file__)) + "\\app\\"
#print("basedir:\t" + str(basedir))

class Config(object):
    SERVER_NAME = None
    SECRET_KEY = os.urandom(24).hex()
    ENABLE_LOG = 0
    TEXT_REGEXP = '[^\u0041-\u005A\u0061-\u007A\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F\u1E00-\u1EFF ]'
    SPACE_REGEXP = '\s{2,}'
    DB_USER = ad_settings.db_user
    DB_PWD = ad_settings.db_pwd
    DB_HOST = ad_settings.db_host
    DB_DB = ad_settings.db_db
    DB_PORT = ad_settings.db_port
    CAR_IMAGES = os.path.join(basedir, 'static\\uploads\\images\\cars')
    CAR_IMG_PATH = 'uploads/images/cars/'
    MEMBER_IMAGES = os.path.join(basedir, 'static\\uploads\\images\\members')
    MEMBER_IMG_PATH = 'uploads/images/members/'
    POST_IMAGES = os.path.join(basedir, 'static\\uploads\\images\\posts')
    POST_IMG_PATH = 'uploads/images/posts/'