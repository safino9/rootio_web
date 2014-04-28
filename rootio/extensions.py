# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.openid import OpenID
oid = OpenID()

from flask.ext.restless import APIManager
rest = APIManager()

from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()

from apscheduler.scheduler import Scheduler
ap_scheduler = Scheduler()

import zmq
zmq_context = zmq.Context()