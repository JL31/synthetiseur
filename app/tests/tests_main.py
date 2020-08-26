"""
    Module to test the several routes of the "main" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

import sys
sys.path.append("../..")

from unittest import TestCase, main

from flask import url_for
from flask_login import current_user

from app import create_app, db
from app.models import User, Article, Reference

from app.auth.forms import LoginForm

from config import Config


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

# =======================
class TestConfig(Config):
    """
        Class to configure the tests
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ELASTICSEARCH_URL = None

# ============================
class TestUserModel(TestCase):
    """
        Class to test the User model
    """

    # ==============
    def setUp(self):
        """
            Method executed before each test
        """

        self.app = create_app(TestConfig)

        self.client = self.app.test_client()

        self.app.config["WTF_CSRF_ENABLED"] = False

        self.app_context = self.app.test_request_context()
        self.app_context.push()

        db.create_all()

        # test user creation into database
        self.test_user = {}
        self.test_user["username"] = "Bob"
        self.test_user["password"] = "bob123456"
        self.test_user["email"] = "dummy data"

        test_user = User(username = self.test_user["username"], email = self.test_user["email"])
        db.session.add(test_user)
        db.session.commit()

        test_user.set_password(self.test_user["password"])
        db.session.commit()

    # =================
    def tearDown(self):
        """
            Method executed after each test
        """

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ==============
    def login(self):
        """
            Method to login the test user (to pass the "login_required" decorator)

            :return: the Response
            :rtype: flask.wrappers.Response
        """

        current_test_user = User.query.filter_by(username = self.test_user["username"]).first()
        log_form = LoginForm(formdata = None, obj = current_test_user)

        log_form.password.data = self.test_user["password"]

        return self.client.post("/auth/login", data = log_form.data, follow_redirects = True)

    # ===============
    def logout(self):
        """
            Method to logout the test user

            :return: the Response
            :rtype: flask.wrappers.Response
        """

        return self.client.get("/auth/logout", follow_redirects = True)

    # ===================
    def test_index(self):
        """
            Method to test the view function for the index page
        """

        with self.client as current_client:

            # preliminary test to check that the current user is anonymous
            self.assertTrue(current_user.is_anonymous)
            
            # test user login tests
            login_response = self.login()

            self.assertEqual(login_response.status_code, 200)
            self.assertFalse(current_user.is_anonymous)
            assert b"Salut Bob !" in login_response.get_data()
            assert not b"Saluttt" in login_response.get_data()

            # root endpoint tests
            response = current_client.get("/", follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_anonymous)
            assert b"Salut Bob !" in response.get_data()
            assert not b"Saluttt" in response.get_data()

            # index endpoint tests
            response = current_client.get("/index", follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_anonymous)
            assert b"Salut Bob !" in response.get_data()
            assert not b"Saluttt" in response.get_data()

            # test user logout tests
            logout_response = self.logout()

            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(current_user.is_anonymous)
            assert b"Bienvenue sur le site du Synthetiseur" in logout_response.get_data()
            assert not b"Salut Bob !" in logout_response.get_data()


    # # ============================
    # def tets_create_article(self):
    #     """

    #     """

    #     with self.client as current_client:

    #         response = current_client.post("/", follow_redirects = True)


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

if __name__ == "__main__":

    main(verbosity = 1)

# https://stackoverflow.com/questions/21577481/flask-wtf-wtforms-with-unittest-fails-validation-but-works-without-unittest
# https://gist.github.com/singingwolfboy/2fca1de64950d5dfed72
# https://stackoverflow.com/questions/10722968/flask-wtf-validate-on-submit-is-never-executed
# https://stackoverflow.com/questions/37579411/testing-a-post-that-uses-flask-wtf-validate-on-submit

# self.app.config["LOGIN_DISABLED"] = True    # to disable the "login_required" decorator

