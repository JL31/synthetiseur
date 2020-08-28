"""
    Module to configuration the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

import os
from dotenv import load_dotenv


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# ==================================================================================================
#
# CLASSES
#
# ==================================================================================================

# ===================
class Config(object):
    """
        Class to set some variables for the application
    """

    # Secret key
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    # Database handling
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail handling
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    ADMINS = os.environ.get("ADMINS")

    # Elasticsearch configuration
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    SEARCH_ARTICLES_PER_PAGE = int(os.environ.get("SEARCH_ARTICLES_PER_PAGE"))

    # OAuth configuration
    OAUTH_CREDENTIALS = {
                         "github": {
                                    "id": os.environ.get("OAUTH_CREDENTIALS_GITHUB_ID"),
                                    "secret" : os.environ.get("OAUTH_CREDENTIALS_GITHUB_SECRET")
                                   }
                        }


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
