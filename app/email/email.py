"""
    Module to handle the email sending through the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask_mail import Message
from flask import render_template, current_app

from app import mail

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

    Thread(target = send_async_email, args = (current_app._get_current_object(), msg)).start()

# =============================
def send_async_email(app, msg):
    """
        Function to send an email asynchronously

        :param app: the Flask application instance
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
