"""
    Module to handle the email sending through the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, current_app
from app.email.email import send_email


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

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# ==================================
def send_password_reset_email(user):
    """
        Function that sends a password reset email to the user

        :param user: the user that asked for password reset
        :type user: app.model.User
    """

    token = user.get_reset_password_token()

    send_email("[Synthétiseur] Réinitialiser ton mot de passe",
               sender = current_app.config["ADMINS"][0],
               recipients = [user.email],
               text_body = render_template("auth/reset_password_message.txt", user = user, token = token),
               html_body = render_template("auth/reset_password_message.html", user = user, token = token))


# ==================================================================================================
#
# USE
#
# ==================================================================================================
