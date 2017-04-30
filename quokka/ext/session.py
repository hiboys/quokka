# coding: utf-8

from flask_session import Session

sess = Session()


def configure(app):
    sess.init_app(app)
