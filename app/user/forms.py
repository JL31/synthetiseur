"""
    Module to handle the several forms for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from app.models import User


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

# =====================================
class UserProfileEditorForm(FlaskForm):
    """
        Class to create a form to edit a user profile
    """

    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    github_login = StringField("Login du compte GitHub")
    email = StringField("Adresse email", validators=[DataRequired(), Email()])
    submit = SubmitField("Mettre à jour")

    # ============================================================================================
    def __init__(self, original_username, original_github_login, original_email, *args, **kwargs):
        """
            Class constructor

            :param original_username: the original username
            :type original_username: str

            :param original_github_login: the original GitHub login
            :type original_github_login: str

            :param original_email: the original email
            :type original_email: str
        """

        super(UserProfileEditorForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_github_login = original_github_login
        self.original_email = original_email

    # ====================================
    def validate_username(self, username):
        """
            Method to validate the new username and to avoid picking existing one

            :param username: the current username field
            :type username: wtforms.fields.core.StringField
        """

        if username.data != self.original_username:

            user = User.query.filter_by(username = self.username.data).first()

            if user is not None:

                raise ValidationError("Ce nom d'utilisateur est déjà pris, merci d'en choisir un autre")

    # ============================================
    def validate_github_login(self, github_login):
        """
            Method to validate the new GitHub login and to avoid picking existing one

            :param github_login: the current GitHub login field
            :type github_login: wtforms.fields.core.StringField
        """

        if github_login.data != self.original_github_login:

            user = User.query.filter_by(github_login = self.github_login.data).first()

            if user is not None:

                raise ValidationError("Ce login est déjà pris, merci d'en choisir un autre")

    # ==============================
    def validate_email(self, email):
        """
            Method to validate the new email and to avoid picking existing one

            :param email: the current email field
            :type email: wtforms.fields.core.StringField
        """

        if email.data != self.original_email:

            user = User.query.filter_by(email = self.email.data).first()

            if user is not None:

                raise ValidationError("Cet email est déjà pris, merci d'en choisir un autre")


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
