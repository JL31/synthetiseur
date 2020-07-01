"""
    Module to handle the several forms for the "main" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


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

# =============================
class CreateArticle(FlaskForm):
    """
        Class to create an a form to add an article
    """

    title = StringField("Titre", validators = [DataRequired()])
    references = StringField("Référence(s)")
    synthesis = TextAreaField("Synthèse", validators = [DataRequired()])
    submit = SubmitField("Ajouter l'article")

# =============================
class ModifyArticle(FlaskForm):
    """
        Class to create an a form to modify an article
    """

    title = StringField("Titre", validators = [DataRequired()])
    references = StringField("Référence(s)")
    synthesis = TextAreaField("Synthèse", validators = [DataRequired()])
    submit = SubmitField("Modifier l'article")

# ==========================
class SearchForm(FlaskForm):
    """
        Class to create a form to do an research among created Article title and synthesis fields values
    """

    q = StringField("Rechercher un article", validators = [DataRequired()])

    # ==================================
    def __init__(self, *args, **kwargs):
        """
            Class constructor
        """

        if "formdata" not in kwargs:

            kwargs["formdata"] = request.args   # because the form will be submitted through GET and not POST

        if "csrf_enabled" not in kwargs:

            kwargs["csrf_enabled"] = False

        super(SearchForm, self).__init__(*args, **kwargs)


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
