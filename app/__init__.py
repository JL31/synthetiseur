"""
    Module to ... the application
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

app = Flask(__name__,
            static_url_path = "/app/static")    # https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = "login"

mail = Mail(app)

bootstrap = Bootstrap(app)

if app.config["ELASTICSEARCH_URL"]:

    app.elasticsearch = Elasticsearch([app.config["ELASTICSEARCH_URL"]])    

else:

    app.elasticsearch = None    


from app import routes, models, errors


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

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

# ==================================================================================================
#
# USE
#
# ==================================================================================================

if not app.debug:

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
