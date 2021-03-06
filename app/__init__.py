#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import settings
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from config import config
from .utils import now

db = SQLAlchemy()
mail = Mail()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main'


def create_app(config_name):
    app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 注册数据库
    db.init_app(app)

    # 注册 Mail
    mail.init_app(app)

    # 注册 LogIn Manager
    login_manager.init_app(app)

    # 注册 APScheduler
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(
        id='auto_check_ports',
        func='app.utils.scheduler:auto_check_ports',
        args=(app,),
        trigger='cron',
        hour='0',
        minute='0',
        second='0'
    )

    # 注册 Logger
    handler = logging.FileHandler('logs/{now}.log'.format(now=now()), encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    # 注册各个 API 接口目录
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .files import file as file_blueprint
    app.register_blueprint(file_blueprint, url_prefix='/files')

    return app
