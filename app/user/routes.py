"""
    Module to handle the several routes for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app import db
from app.models import User, Article

from app.user import bp
from app.user.forms import UserProfileEditorForm


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

# ============================
@bp.route("/user/<username>")
@login_required
def user(username):
    """
        View function for a User to see its profile

        :param username: the current username
        :type username: str

        :return: the view to be displayed
        :rtype: str
    """

    if username == "invite":

        return redirect(url_for("main.index"))

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    user = User.query.filter_by(username = username).first_or_404()

    if user == current_user:

        return render_template("user/user.html", user = user)

    else:

        return render_template("main/acces_denied.html")

# ============================================================
@bp.route("/user_profile_edition", methods = ["GET", "POST"])
@login_required
def user_profile_edition():
    """
        View function for a User to edit its profile

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    form = UserProfileEditorForm(current_user.username)

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()

        flash("Ton profil a bien été mis-à-jour")

        return redirect(url_for("user.user", username = current_user.username))

    elif request.method == "GET":

        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("user/user_profile_editor.html",
                           title = "Modifier mon profil",
                           form = form)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
