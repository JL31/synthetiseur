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

from json import loads


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
class TestMain(TestCase):
    """
        Class to test the "main" blueprint several routes
    """

    # ==============
    def setUp(self):
        """
            Method executed before each test
        """

        # value of the associated "url_prefix" blueprint option
        self.url_prefix = ""

        self.app = create_app(TestConfig)

        self.client = self.app.test_client()

        self.app.config["WTF_CSRF_ENABLED"] = False

        self.app_context = self.app.test_request_context()
        self.app_context.push()

        db.create_all()

        # test user creation into database
        self.test_user = {}
        self.test_user["username"] = "Bob"
        self.test_user["github_login"] = "git-test"
        self.test_user["email"] = "dummy data"
        self.test_user["password"] = "bob123456"

        test_user = User(username = self.test_user["username"],
                         github_login = self.test_user["github_login"],
                         email = self.test_user["email"])
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
            assert "Salut Bob !" in login_response.get_data().decode("utf-8")
            assert not "Saluttt" in login_response.get_data().decode("utf-8")

            # root endpoint tests
            response = current_client.get(self.get_path("/"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_anonymous)
            assert "Salut Bob !" in response.get_data().decode("utf-8")
            assert not "Saluttt" in response.get_data().decode("utf-8")

            # index endpoint tests
            response = current_client.get(self.get_path("/index"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_anonymous)
            assert "Salut Bob !" in response.get_data().decode("utf-8")
            assert not "Saluttt" in response.get_data().decode("utf-8")

            # test user logout tests
            logout_response = self.logout()

            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(current_user.is_anonymous)
            assert "Bienvenue sur le site du Synthetiseur" in logout_response.get_data().decode("utf-8")
            assert not "Salut Bob !" in logout_response.get_data().decode("utf-8")

    # ============================
    def test_create_article(self):
        """
            Method to create an article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # create_article endpoint test
            response = current_client.get(self.get_path("/create_article"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert "Créer un article" in response.get_data().decode("utf-8")

            # test article creation
            data = {
                    "title": "Titre de test",
                    "synthesis": "Synthèse de test"
                   }
            current_client.post(self.get_path("/create_article"), data = data)

            # test articles without reference tests
            test_article = Article.query.all()[0]

            self.assertEqual(test_article.title, "Titre de test")
            self.assertEqual(test_article.synthesis, "Synthèse de test")

            # test articles with reference test
            test_reference = Reference(description = "www.bidon.fr", article = test_article)
            db.session.commit()

            test_article = Article.query.all()[0]
            reference = test_article.references.all()[0]

            self.assertEqual(reference.description, "www.bidon.fr")

    # ================================
    def test_user_articles_list(self):
        """
            Method to see the list of articles for a given User
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # user_articles_list endpoint test
            response = current_client.get(self.get_path("/user_articles_list"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert "Liste de mes articles" in response.get_data().decode("utf-8")

            # addition of some articles
            data = [
                    {
                     "title": "Titre de test 1",
                     "synthesis": "Synthèse de test 1"
                    },
                    {
                     "title": "Titre de test 2",
                     "synthesis": "Synthèse de test 2"
                    },
                    {
                     "title": "Titre de test 3",
                     "synthesis": "Synthèse de test 3"
                    }
                   ]

            for set_of_data in data:

                current_client.post(self.get_path("/create_article"), data = set_of_data)

            # test of article addition in the list of articles
            response = current_client.get(self.get_path("/user_articles_list"), follow_redirects = True)

            for set_of_data in data:

                assert set_of_data["title"] in response.get_data().decode("utf-8")

    # =====================
    def test_article(self):
        """
            Method to consult a specific article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of some articles
            data = [
                    {
                     "title": "Titre de test 1",
                     "synthesis": "Synthèse de test 1"
                    },
                    {
                     "title": "Titre de test 2",
                     "synthesis": "Synthèse de test 2"
                    },
                    {
                     "title": "Titre de test 3",
                     "synthesis": "Synthèse de test 3"
                    }
                   ]

            for set_of_data in data:

                current_client.post(self.get_path("/create_article"), data = set_of_data)

            # tests
            for article_index, set_of_data in enumerate(data):

                response = current_client.get(self.get_path("/article/{}".format(article_index + 1)), follow_redirects = True)
                
                # user_articles_list endpoint test
                self.assertEqual(response.status_code, 200)

                # correct title
                assert set_of_data["title"] in response.get_data().decode("utf-8")

                # correct synthesis
                assert set_of_data["synthesis"] in response.get_data().decode("utf-8")

    # ============================
    def test_modify_article(self):
        """
            Method to modify an article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of an article
            data = {
                    "title": "Titre de test",
                    "synthesis": "Synthèse de test"
                   }

            current_client.post(self.get_path("/create_article"), data = data)

            # test modification without changing anything
            response = current_client.get(self.get_path("/modify_article/1"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data["title"] in response.get_data().decode("utf-8")
            assert data["synthesis"] in response.get_data().decode("utf-8")

            # test modification with title modification
            data = {
                    "title": "Titre de test modifié",
                    "synthesis": "Synthèse de test"
                   }

            response = current_client.post(self.get_path("/modify_article/1"), data = data, follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data["title"] in response.get_data().decode("utf-8")
            assert data["synthesis"] in response.get_data().decode("utf-8")

            # test modification with synthesis modification
            data = {
                    "title": "Titre de test",
                    "synthesis": "Synthèse de test modifiée"
                   }

            response = current_client.post(self.get_path("/modify_article/1"), data = data, follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data["title"] in response.get_data().decode("utf-8")
            assert data["synthesis"] in response.get_data().decode("utf-8")

    # ============================
    def test_delete_article(self):
        """
            Method to delete an article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of an article
            data = {
                    "title": "Titre de test",
                    "synthesis": "Synthèse de test"
                   }

            current_client.post(self.get_path("/create_article"), data = data)

            # check if previously created article exists
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # previously created article deletion
            current_client.get(self.get_path("/delete_article/1"), follow_redirects = True)

            # check if article deletion succeeded (through article direct access)
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)
            self.assertEqual(response.status_code, 404)

            # check if article deletion succeeded (through article list access)
            response = current_client.get(self.get_path("/user_articles_list"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data["title"] not in response.get_data().decode("utf-8")

    # ===========================
    def test_add_reference(self):
        """
            Method to add a reference to an article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of an article
            data_article = {
                            "title": "Titre de test",
                            "synthesis": "Synthèse de test"
                           }

            current_client.post(self.get_path("/create_article"), data = data_article)

            # check if article has been created
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data_article["title"] in response.get_data().decode("utf-8")
            assert data_article["synthesis"] in response.get_data().decode("utf-8")

            # current user, test article and article references objects retrieval
            current_test_user = User.query.all()[0]
            test_article = Article.query.all()[0]
            article_references = test_article.references.all()

            # check if previously created article possess references
            self.assertFalse(article_references)    # False because this variable is an empty list

            # reference addition to previously created article
            data_reference = { "references": "http://www.bidon.fr" }
            current_client.post(self.get_path("/add_reference/{}/{}".format(
                                                                            current_test_user.id,
                                                                            test_article.id
                                                                           )
                                             ),
                                data = data_reference
                               )

            # article references object retrieval
            article_references = test_article.references.all()

            # check if previously created article possess references
            self.assertTrue(article_references)     # True because this variable is NOT an empty list

            # check if reference has been added to previously created article
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data_article["title"] in response.get_data().decode("utf-8")
            assert data_article["synthesis"] in response.get_data().decode("utf-8")
            assert data_reference["references"] in response.get_data().decode("utf-8")

    # ==============================
    def test_delete_reference(self):
        """
            Method to delete a reference from an article
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of an article
            data_article = {
                            "title": "Titre de test",
                            "synthesis": "Synthèse de test"
                           }

            current_client.post(self.get_path("/create_article"), data = data_article)

            # current user and test article objects retrieval
            current_test_user = User.query.all()[0]
            test_article = Article.query.all()[0]

            # reference addition to previously created article
            data_reference = { "references": "http://www.bidon.fr" }
            current_client.post(self.get_path("/add_reference/{}/{}".format(
                                                                            current_test_user.id,
                                                                            test_article.id
                                                                           )
                                             ),
                                data = data_reference
                               )

            # article references object retrieval
            article_references = test_article.references.all()

            # check if previously created article possess references
            self.assertTrue(article_references)     # True because this variable is NOT an empty list

            # check if reference has been added to previously created article
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data_reference["references"] in response.get_data().decode("utf-8")

            # delete the previously added reference to the previously created article
            response = current_client.get(self.get_path(f"/delete_reference/{article_references[0].id}/{test_article.id}"), follow_redirects = True)            
            self.assertEqual(response.status_code, 200)

            # article references object retrieval
            article_references = test_article.references.all()

            # check if previously created article possess references
            self.assertFalse(article_references)    # False because this variable is an empty list

            # check if reference has been added to previously created article
            response = current_client.get(self.get_path("/article/1"), follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            assert data_reference["references"] not in response.get_data().decode("utf-8")

    # =================================
    def test_check_article_title(self):
        """
            Method to check if the current article title is already taken
        """

        with self.client as current_client:

            # test user login
            login_response = self.login()

            # addition of an article
            data_article = {
                            "title": "Titre de test",
                            "synthesis": "Synthèse de test"
                           }

            current_client.post(self.get_path("/create_article"), data = data_article)

            # test to check the article title with already existing title
            response = current_client.post(self.get_path("/check_article_title"), data = data_article)

            self.assertEqual(response.status_code, 200)
            returned_data = loads(response.get_data().decode("utf-8"))
            self.assertTrue(returned_data["title_already_exists"])

            # test to check the article title with non existing title
            response = current_client.post(self.get_path("/check_article_title"), data = {"title": "test title"})

            self.assertEqual(response.status_code, 200)
            returned_data = loads(response.get_data().decode("utf-8"))
            self.assertFalse(returned_data["title_already_exists"])


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

