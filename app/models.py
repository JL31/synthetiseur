"""
    Module to handle the several models for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from app import db, app, login
from app.search import add_to_index, remove_from_index, query_index
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime
from time import time
import jwt


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

# ============================
class SearchableMixin(object):
    """
        Class to make the link between an SQLAlchemy model and the Elasticsearch module
    """

    # =========================================
    @classmethod
    def search(cls, expression, page, per_page):
        """
            Class method to execute an Elasticsearch search of the input "expression"
            for the associated input "cls" (with input options values "page" and "per_page")

            :param cls: a class
            :type cls: class

            :param expression: the searched text 
            :type expression: str

            :param page: the page number from the query results
            :type page: int

            :param per_page: the number of results per page from the query results
            :type per_page: int

            :return: ...
            :rtype: tuple(, int)
        """

        ids, total = query_index(cls.__tablename__, expression, page, per_page)

        if total == 0:

            return cls.query.filter_by(id = 0), 0

        when = []

        # for i in range(len(ids)):

        #     when.append((ids[i], i))
        for list_index, list_value in enumerate(ids):

            when.append((list_value, list_index))

        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value = cls.id)), total

    # ==============================
    @classmethod
    def before_commit(cls, session):
        """
            Class method to save the objects that are going to be :

            - added ("new")
            - modified ("dirty")
            - removed ("deleted")

            :param cls: a class
            :type cls: class

            :param session: a session
            :type session: ...

            :return: Nothing
            :rtype: None
        """

        session._changes = { "add": list(session.new),
                             "update": list(session.dirty),
                             "delete": list(session.deleted)
                           }

    # =============================
    @classmethod
    def after_commit(cls, session):
        """
            Class method to make changes on the Elasticsearch side,
            i.e. to call the corresponding indexing function depending on the case
            (add, modify or delete)

            :param cls: a class
            :type cls: class

            :param session: a session
            :type session: ..

            :return: nothing
            :rtype: None
        """

        for obj in session._changes["add"]:

            if isinstance(obj, SearchableMixin):

                add_to_index(obj.__tablename__, obj)

        for obj in session._changes["update"]:

            if isinstance(obj, SearchableMixin):

                add_to_index(obj.__tablename__, obj)

        for obj in session._changes["delete"]:

            if isinstance(obj, SearchableMixin):

                remove_from_index(obj.__tablename__, obj)

        session._changes = None

    # ===============
    @classmethod
    def reindex(cls):
        """
            Class method to refresh an index 

            :param cls: a class
            :type cls: class

            :return: ...
            :rtype: ...
        """

        for obj in cls.query:

            add_to_index(cls.__tablename__, obj)

# ==============================
class User(UserMixin, db.Model):
    """
        Class that represents a User
    """

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    articles = db.relationship("Article", backref = "author", lazy = "dynamic")

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<User {}>".format(self.username)

    # ===============================
    def set_password(self, password):
        """
            Method to define the password

            :param password: the value of the password
            :type password: str
        """

        self.password_hash = generate_password_hash(password)

    # ===============================
    def check_password(self, password):
        """
            Method to check the password

            :param password: the value of the password
            :type password: str

            :return: return the result of the password check
            :rtype: bool
        """

        return check_password_hash(self.password_hash, password)

    # ===================================================
    def get_reset_password_token(self, expires_in = 600):
        """
            Method that generates a token for the reset password procedure

            :param expires_in: expiration delay (in seconds)
            :type expires_in: int

            :return: the token
            :rtype: str
        """

        return jwt.encode({ "reset_password": self.id,
                            "exp": time() + expires_in
                          },
                          app.config["SECRET_KEY"],
                          algorithm = "HS256").decode("utf-8")

    # =====================================
    @staticmethod
    def verify_reset_password_token(token):
        """
            Function to check the token within the reset password procedure

            :param token: the token to be checked
            :type token: str

            :return: None if the token cannot be validated or is expired, else the associated User
            :rtype: None | app.model.User
        """

        try:

            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms = ["HS256"])["reset_password"]

        except:

            return None

        return User.query.get(id)

# =======================================
class Article(SearchableMixin, db.Model):
    """
        Class that represents an Article
    """

    __searchable__ = ["title", "synthesis"]

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), index = True, unique = True)
    references = db.relationship("Reference", backref = "article", lazy = "dynamic", cascade="all,delete")
    creation_date = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    update_date = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    synthesis = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<Article {}>".format(self.title)

# ========================
class Reference(db.Model):
    """
        Class that represents a Reference
    """

    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(100), index = True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<Reference {}>".format(self.description)

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# =====================
@login.user_loader
def load_user(user_id):
    """
        Function to load a user through its id

        :param user_id: the id of a user
        :type user_id: int

        :return: an instance of the User class
        :rtype: app.models.User
    """

    return User.query.get(user_id)


# ==================================================================================================
#
# USE
#
# ==================================================================================================

db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)
