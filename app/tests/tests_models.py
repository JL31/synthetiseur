"""
    Module to test the several application models
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
from app.models import User, Article, Reference

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
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    # =================
    def tearDown(self):
        """
            Method executed after each test
        """

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ===========================
    def test_user_creation(self):
        """
            Method to test the creation of a User
        """

        test_user_1 = User(username = "Bob", email = "dummy data")

        db.session.add(test_user_1)
        db.session.commit()

        self.assertEqual(test_user_1.username, "Bob")
        self.assertEqual(test_user_1.email, "dummy data")
        self.assertEqual(test_user_1.is_guest, False)

        test_user_2 = User(username = "Bobinette", email = "dummy data 2", is_guest = True)

        self.assertEqual(test_user_2.username, "Bobinette")
        self.assertEqual(test_user_2.email, "dummy data 2")
        self.assertEqual(test_user_2.is_guest, True)

    # ==============================
    def test_password_hashing(self):
        """
            Test of the password hashing :

            - "set_password" method
            - "check_password" method
        """

        test_user = User(username = "Bob", email = "dummy data")
        test_user.set_password("bob123456")

        self.assertFalse(test_user.check_password("tot"))
        self.assertTrue(test_user.check_password("bob123456"))

    # ============================================
    def test_reset_password_token_procedure(self):
        """
            Test of the password reset token prodecude
        """

        test_user = User(username = "Bob", email = "dummy data")

        db.session.add(test_user)
        db.session.commit()

        test_user_token = test_user.get_reset_password_token()

        fake_token = "abcde12345"

        self.assertEqual(User.verify_reset_password_token(fake_token), None)
        self.assertEqual(User.verify_reset_password_token(test_user_token), test_user)

    # =====================
    def test_to_dict(self):
        """
            Test of the "to_dict" method
        """

        test_user = User(username = "Bob", email = "dummy data")

        db.session.add(test_user)
        db.session.commit()

        data = {}
        data = {
                "id": 1,
                "username": "Bob",
                "is_guest": False,
                "_links": {
                           "self": "/api/users/1",
                           "articles": "/api/articles/1"
                          }
               }

        self.app_context = self.app.test_request_context()
        self.app_context.push()

        self.assertEqual(test_user.to_dict(), data)

        data["email"] = "dummy data"

        self.assertEqual(test_user.to_dict(include_email = True), data)

    # =======================
    def test_from_dict(self):
        """
            Test of the "from_dict" method
        """

        test_user = User()

        data = {
                "username": "Bob",
                "email": "dummy data",
                "is_guest": False,
               }

        test_user.from_dict(data, new_user = True)

        self.assertEqual(test_user.username, "Bob")
        self.assertEqual(test_user.email, "dummy data")
        self.assertEqual(test_user.is_guest, False)

        data = {
                "username": "Bobinette",
                "email": "dummy data 2",
                "password": "bobinette123456",
                "is_guest": True,
               }

        test_user.from_dict(data, new_user = True)

        self.assertEqual(test_user.username, "Bobinette")
        self.assertEqual(test_user.email, "dummy data 2")
        self.assertTrue(test_user.check_password("bobinette123456"))
        self.assertEqual(test_user.is_guest, True)

        data = {
                "username": "Bobby",
                "email": "dummy data",
                "is_guest": False,
               }

        test_user.from_dict(data)

        self.assertEqual(test_user.username, "Bobby")
        self.assertEqual(test_user.email, "dummy data")
        self.assertEqual(test_user.is_guest, False)

        data = {
                "username": "Bob",
                "email": "dummy data 3",
                "is_guest": False
               }

        test_user.from_dict(data)

        self.assertEqual(test_user.username, "Bob")
        self.assertEqual(test_user.email, "dummy data 3")
        self.assertEqual(test_user.is_guest, False)

    # =================================
    def test_API_token_procedure(self):
        """
            Method to test the token procedure (normally through APIs)
        """

        test_user = User(username = "Bob", email = "dummy data")
        test_user_token = test_user.get_token()

        self.assertEqual(User.check_token("fake_token_123"), None)
        self.assertEqual(User.check_token(test_user_token), test_user)

        test_user.revoke_token()

        self.assertEqual(User.check_token(test_user_token), None)

# ===============================
class TestArticleModel(TestCase):
    """
        Class to test the Article model
    """

    # ==============
    def setUp(self):
        """
            Method executed before each test
        """

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    # =================
    def tearDown(self):
        """
            Method executed after each test
        """

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ===========================
    def test_article_creation(self):
        """
            Method to test the creation of an Article
        """

        test_user = User(username = "Bob", email = "dummy data")
        db.session.add(test_user)
        db.session.commit()

        test_article = Article(title = "Test 1", synthesis = "Synthèse", user_id = test_user.id)
        db.session.add(test_article)
        db.session.commit()

        self.assertEqual(test_article.title, "Test 1")
        self.assertEqual(test_article.synthesis, "Synthèse")
        self.assertEqual(test_article.user_id, test_user.id)

    # =====================
    def test_to_dict(self):
        """
            Test of the "to_dict" method
        """

        test_user = User(username = "Bob", email = "dummy data")
        db.session.add(test_user)
        db.session.commit()

        test_article = Article(title = "Test 1", synthesis = "Synthèse", user_id = test_user.id)
        db.session.add(test_article)
        db.session.commit()

        data = {}
        data = {
                "id": 1,
                "title": "Test 1",
                "synthesis": "Synthèse",
               }

        returned_data = test_article.to_dict()

        self.assertEqual(returned_data["id"], data["id"])
        self.assertEqual(returned_data["title"], data["title"])
        self.assertEqual(returned_data["synthesis"], data["synthesis"])

    # =======================
    def test_from_dict(self):
        """
            Test of the "from_dict" method
        """

        test_user = User(username = "Bob", email = "dummy data")
        db.session.add(test_user)
        db.session.commit()

        test_article = Article(user_id = test_user.id)
        db.session.add(test_article)
        db.session.commit()

        data = {}
        data = {
                "title": "Test 1",
                "synthesis": "Synthèse",
               }

        test_article.from_dict(data, new_article = True)

        self.assertEqual(test_article.title, data["title"])
        self.assertEqual(test_article.synthesis, data["synthesis"])

        data = {
                "title": "Test 2",
                "synthesis": "Synthèse",
               }

        test_article.from_dict(data, new_article = False)

        self.assertEqual(test_article.title, data["title"])
        self.assertEqual(test_article.synthesis, data["synthesis"])

        data = {
                "title": "Test",
                "synthesis": "Synthèse 2",
               }

        test_article.from_dict(data, new_article = False)

        self.assertEqual(test_article.title, data["title"])
        self.assertEqual(test_article.synthesis, data["synthesis"])

# =================================
class TestReferenceModel(TestCase):
    """
        Class to test the Reference model
    """

    # ==============
    def setUp(self):
        """
            Method executed before each test
        """

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    # =================
    def tearDown(self):
        """
            Method executed after each test
        """

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ===========================
    def test_reference_creation(self):
        """
            Method to test the creation of a Reference
        """

        test_user = User(username = "Bob", email = "dummy data")
        db.session.add(test_user)
        db.session.commit()

        test_article = Article(title = "Test 1", synthesis = "Test", user_id = test_user.id)
        db.session.add(test_article)
        db.session.commit()

        test_reference = Reference(description = "www.bidon.fr", article = test_article)

        db.session.add(test_reference)
        db.session.commit()

        self.assertEqual(test_reference.description, "www.bidon.fr")
        self.assertEqual(test_reference.article, test_article)


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

if __name__ == '__main__':

    main(verbosity = 1)
