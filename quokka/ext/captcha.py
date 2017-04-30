# coding: utf-8

from flask_captcha import Captcha
from flask_captcha.views import captcha_blueprint
from flask_captcha.models import db
from flask_sqlalchemy import SQLAlchemy

app_captcha = Captcha()

def configure(app):
    app.register_blueprint(captcha_blueprint, url_prefix='/captcha')
    app.config.from_object("flask_captcha.settings")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
    app_captcha.init_app(app)
