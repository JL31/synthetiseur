"""
    Module to handle the email sending through the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask_mail import Message
from flask import render_template
from app import app, mail
from threading import Thread


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
               sender = app.config["ADMINS"][0],
               recipients = [user.email],
               text_body = render_template("email/reset_password_message.txt", user = user, token = token),
               html_body = render_template("email/reset_password_message.html", user = user, token = token))

# ================================================================
def send_email(subject, sender, recipients, text_body, html_body):
    """
        Function that enables to send email

        :param subject: the email subject
        :type subject: str

        :param sender: the email sender
        :type sender: str

        :param recipients: the email recipients
        :type recipients: str

        :param text_body: the email body (plain text version)
        :type text_body: str

        :param html_body: the email body (HTML version)
        :type html_body: str
    """

    msg = Message(subject, sender = sender, recipients = recipients)

    msg.body = text_body
    msg.html = html_body

    Thread(target = send_async_email, args = (app, msg)).start()

# =============================
def send_async_email(app, msg):
    """
        Function to send an email asynchronously

        :param app: the application instance
        :type app: flask.app.Flask

        :param msg: the message to be sent by email
        :type msg: str
    """

    with app.app_context():

        mail.send(msg)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
