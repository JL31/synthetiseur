"""
    Module to handle the several routes for the "auth" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user

from werkzeug.urls import url_parse

from app import db

from app.models import User, Article

from app.auth import bp
from app.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email


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

# =============================================
@bp.route("/login", methods = ["GET", "POST"])
def login():
    """
        View function to login

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username = form.username.data).first()

        if user is None or not user.check_password(form.password.data):

            flash("Nom d'utilisateur ou mot de passe incorrect")
            return redirect(url_for("auth.login"))

        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get("next")

        if not next_page or url_parse(next_page).netloc != "":

            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("auth/login.html", title = "Connexion", form = form)

# ===================
@bp.route("/logout")
def logout():
    """
        View function to logout

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    logout_user()

    return redirect(url_for("auth.login"))

# ==============================================================
@bp.route("/reset_password_request", methods = ["GET", "POST"])
def reset_password_request():
    """
        View function for a User to ask for a password reset

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    if current_user.is_authenticated:

        return redirect(url_for("main.index"))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email = form.email.data).first()

        if user:

            send_password_reset_email(user)

        flash("Un email t'a été envoyé avec les instructions afin de réinitialiser ton mot de passe")

        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password_request.html",
                           title = "Réinitialisation du mot de passe",
                           form = form)

# ==============================================================
@bp.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_password(token):
    """
        View function for a User to reset his password

        :param token: the token generated during the password reset process
        :type token: str

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    if current_user.is_authenticated:

        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)

    if not user:

        flash("Jeton invalide : le lien a peut-être expiré")
        return redirect(url_for("main.index"))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        user.set_password(form.password.data)
        db.session.commit()

        flash("Ton mot de passe a bien été réinitialisé")

        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form = form)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
