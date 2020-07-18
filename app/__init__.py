"""
    Module to initialize the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

# extensions instances creation
# =============================

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
bootstrap = Bootstrap()

login.login_view = "auth.login"


# ==================================================================================================
#
# CLASSES
#
# ==================================================================================================

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# ====================================
def create_app(config_class = Config):
    """
        Function to create an instance of the Flask application

        :param config_class: ...
        :type config_class: ...

        :return: ...
        :rtype: ...
    """

    # application instance creation
    # =============================

    app = Flask(__name__, static_url_path = "/app/static")    # https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
    app.config.from_object(config_class)


    # extensions instances initialization
    # ===================================

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)


    # elasticsearch configuration
    # ===========================

    if app.config["ELASTICSEARCH_URL"]:

        app.elasticsearch = Elasticsearch([app.config["ELASTICSEARCH_URL"]])    

    else:

        app.elasticsearch = None    


    # blueprints registration
    # =======================

    # "errors" blueprint
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # "auth" blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix = "/auth")

    # "user" blueprint
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix = "/user")

    # "email" blueprint
    from app.email import bp as email_bp
    app.register_blueprint(email_bp)

    # "main" blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # "api" blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix = "/api")


    # logging definition
    # ==================

    if not app.debug and not app.testing:

        # Sending errors by email
        if app.config["MAIL_SERVER"]:

            auth = None

            if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:

                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])

            secure = None

            if app.config["MAIL_USE_TLS"]:

                secure = ()

            mail_handler = SMTPHandler(mailhost = (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                                       fromaddr = "no-reply@" + app.config["MAIL_SERVER"],
                                       toaddrs = app.config["ADMINS"],
                                       subject = "[Synthétiseur] Problème",
                                       credentials = auth,
                                       secure = secure)

            mail_handler.setLevel(logging.ERROR)

            app.logger.addHandler(mail_handler)

        # Logging to a file
        if not os.path.exists("logs"):

                os.mkdir("logs")

        file_handler = RotatingFileHandler("logs/Synthetiseur.log", maxBytes = 10240, backupCount = 10)
        file_formatter = logging.Formatter("<< %(levelname)s >> [ file \"%(pathname)s\" line %(lineno)d ] @ %(asctime)s --> %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Synthetiseur startup")


    # function return
    # ===============

    return app


# ==================================================================================================
#
# USE
#
# ==================================================================================================

# models imports
# ==============

from app import models

