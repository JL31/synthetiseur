"""
    Module to handle the several forms for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
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

# =========================
class LoginForm(FlaskForm):
    """
        Class to create the login form
    """

    username = StringField("Nom d'utilisateur", validators = [DataRequired()])
    password = PasswordField("Mot de passe", validators = [DataRequired()])
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Connexion")

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

# =============================
class CreateArticle(FlaskForm):
    """
        Class to create an a form to add an article
    """

    title = StringField("Titre", validators = [DataRequired()])
    keywords = StringField("Mot(s) clé(s)")
    references = StringField("Référence(s)")
    synthesis = TextAreaField("Synthèse", validators = [DataRequired()])
    submit = SubmitField("Ajouter l'article")

# =============================
class ModifyArticle(FlaskForm):
    """
        Class to create an a form to modify an article
    """

    title = StringField("Titre", validators = [DataRequired()])
    keywords = StringField("Mot(s) clé(s)")
    references = StringField("Référence(s)")
    synthesis = TextAreaField("Synthèse", validators = [DataRequired()])
    submit = SubmitField("Mdofier l'article")

# ========================================
class ResetPasswordRequestForm(FlaskForm):
    """
        Class to create a form to ask for a password resset
    """

    email = StringField("Email", validators = [DataRequired(), Email()])
    submit = SubmitField("Demander un nouveau mot de passe")

# =================================
class ResetPasswordForm(FlaskForm):
    """
        Class to create a form to ask for a new password (within the context of a reset password)
    """

    password = PasswordField("Mot de passe", validators = [DataRequired()])
    password2 = PasswordField("Confirme le mot de passe", validators = [DataRequired(), EqualTo("password", "Les mots de passe doivent être identiques")])
    submit = SubmitField("Réinitialiser le mot de passe")

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
