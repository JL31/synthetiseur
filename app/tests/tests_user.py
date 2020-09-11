"""
    Module to test the several routes of the "user" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

import sys
sys.path.append("../..")

from unittest import TestCase, main

from app import create_app, db
from app.models import User

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

# =======================
class TestUser(TestCase):
    """
        Class to test the several routes of the "user" blueprint
    """

    # ==============
    def setUp(self):
        """
            Method executed before each test
        """

        # value of the associated "url_prefix" blueprint option
        self.url_prefix = "/user"

        self.app = create_app(TestConfig)

        self.client = self.app.test_client()

        self.app.config["WTF_CSRF_ENABLED"] = False

        self.app_context = self.app.test_request_context()
        self.app_context.push()

        db.create_all()

        # test user creation into database
        self.test_user_1 = {
                            "username": "Bob",
                            "github_login": "git-test",
                            "email": "a.b@c.fr",
                            "password": "bob123456"
                           }

        test_user_1 = User(username = self.test_user_1["username"],
                           github_login = self.test_user_1["github_login"],
                           email = self.test_user_1["email"])
        db.session.add(test_user_1)
        db.session.commit()

        test_user_1.set_password(self.test_user_1["password"])
        db.session.commit()

        # test user 2 creation into database
        self.test_user_2 = {
                            "username": "Toto",
                            "github_login": "git-tut",
                            "email": "aa.bb@c.fr",
                            "password": "toto123456"
                           }

        test_user_2 = User(username = self.test_user_2["username"],
                           github_login = self.test_user_2["github_login"],
                           email = self.test_user_2["email"])
        db.session.add(test_user_2)
        db.session.commit()

        test_user_2.set_password(self.test_user_2["password"])
        db.session.commit()

    # =================
    def tearDown(self):
        """
            Method executed after each test
        """

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ======================
    def get_path(self, url):
        """
            Method to create the path for the request (GET or POST)

            This method concatenate :

            - the value of the "url_prefix" attribute (if not empty)
            - the "url" input value

            This is useful in case a bluprint as the "url_prefix" attribute not empty

            :param url: the URL to be concatenated
            :type url: str

            :return: the complete URL with the "url_prefix" value
            :rtype: str
        """

        return "{}{}".format(self.url_prefix, 
                             url)

    # =============================
    def login(self, specific_user):
        """
            Method to login the a test user (to pass the "login_required" decorator)

            :param specific_user: the test user to login 
            :type specific_user: dict
        """

        current_test_user = User.query.filter_by(username = specific_user["username"]).first()
        log_form = LoginForm(formdata = None, obj = current_test_user)

        log_form.password.data = specific_user["password"]

        self.client.post("/auth/login", data = log_form.data, follow_redirects = True)

    # ===============
    def logout(self):
        """
            Method to logout logged in test user
        """

        self.client.get("/auth/logout", follow_redirects = True)

    # ==================
    def test_user(self):
        """
            Method for a User to consult its profile data
        """

        with self.client as current_client:

            # current user definition
            current_user = self.test_user_1

            # test user login tests
            self.login(current_user)

            # root endpoint tests
            response = current_client.get(self.get_path("/" + current_user["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # user profile data check
            data_response = response.get_data().decode("utf-8")

            assert current_user["username"] in data_response
            assert current_user["github_login"] in data_response
            assert current_user["email"] in data_response

    # ==================================
    def test_user_profile_edition(self):
        """
            Method to modify the user profile data
        """

        with self.client as current_client:

            # current user definition
            current_user = self.test_user_1

            # test user login tests
            self.login(current_user)

            # root endpoint tests
            response = current_client.get(self.get_path("/user_profile_edition"), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # user profile data check
            data_response = response.get_data().decode("utf-8")

            assert 'value="{}"'.format(current_user["username"]) in data_response
            assert 'value="{}"'.format(current_user["github_login"]) in data_response
            assert 'value="{}"'.format(current_user["email"]) in data_response


            # username modification
            # =====================

            # modification
            data = {
                     "username": "Bob modifié",
                     "github_login": current_user["github_login"],
                     "email": current_user["email"]
                   }

            current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)

            # username modification checks
            
                # check that previous user no longer exists
            response = current_client.get(self.get_path("/" + current_user["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 404)

                # check that new user exists
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

                # check new user profile data
            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert data["email"] in data_response


            # email modification
            # ==================

            # valid and not already existing email modification
            # -------------------------------------------------

            data = {
                     "username": "Bob modifié",
                     "github_login": current_user["github_login"],
                     "email": "d.e@f.fr"
                   }

            current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # email modification checks
            
                # check that new user exists
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

                # check new user profile data
            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert data["email"] in data_response


            # invalid email "modification"
            # ----------------------------

            data = {
                     "username": "Bob modifié",
                     "github_login": current_user["github_login"],
                     "email": "dummy data"
                   }

            # modification attempt
            response = current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # modification checks
            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert data["email"] in data_response
            assert "Invalid email address." in data_response

            # modification failure check 
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert "d.e@f.fr" in data_response


            # already existing email modification
            # -----------------------------------

            # current user definition
            current_user = self.test_user_2

            # test user login tests
            self.logout()
            self.login(current_user)

            response = current_client.get(self.get_path("/" + current_user["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data = {
                     "username": current_user["username"],
                     "github_login": current_user["github_login"],
                     "email": "d.e@f.fr"
                   }

            # modification attempt
            response = current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # modification checks
            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert data["email"] in data_response
            assert "Cet email est déjà pris, merci d&#39;en choisir un autre" in data_response

            # modification failure check 
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert current_user["email"] in data_response


            # github_login modification
            # =========================

            # non empty and not already taken
            # -------------------------------

            data = {
                     "username": current_user["username"],
                     "github_login": "tut",
                     "email": current_user["email"]
                   }

            # modification
            response = current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # modification checks
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert data["email"] in data_response


            # non empty and already taken
            # ---------------------------

            data = {
                     "username": current_user["username"],
                     "github_login": self.test_user_1["github_login"],
                     "email": current_user["email"]
                   }

            # modification attempt
            response = current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # modification checks
            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert data["github_login"] in data_response
            assert "Ce login est déjà pris, merci d&#39;en choisir un autre" in data_response
            assert data["email"] in data_response

            # modification failure check 
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert "tut" in data_response
            assert current_user["email"] in data_response

            # empty
            # -----

            data = {
                     "username": current_user["username"],
                     "github_login": "",
                     "email": current_user["email"]
                   }

            # modification
            response = current_client.post(self.get_path("/user_profile_edition"), data = data, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # modification checks
            response = current_client.get(self.get_path("/" + data["username"]), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            data_response = response.get_data().decode("utf-8")

            assert data["username"] in data_response
            assert "*** pas de login indiqué ***" in data_response
            assert data["email"] in data_response


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

