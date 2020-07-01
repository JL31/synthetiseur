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
    email = StringField("Adresse email", validators=[DataRequired(), Email()])
    submit = SubmitField("Mettre à jour")

    # =====================================================
    def __init__(self, original_username, *args, **kwargs):
        """
            Class constructor

            :param original_username: the original username
            :type original_username: str
        """

        super(UserProfileEditorForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

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
