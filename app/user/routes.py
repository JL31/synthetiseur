"""
    Module to handle the several routes for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required

from app import db
from app.models import User, Article

from app.user import bp
from app.user.forms import UserProfileEditorForm

from string import ascii_letters, digits
from random import choices


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
@bp.route("/<username>")
@login_required
def user(username):
    """
        View function for a User to see its profile

        :param username: the current username
        :type username: str

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_guest:

        return redirect(url_for("main.index"))

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    user = User.query.filter_by(username = username).first_or_404()

    if user == current_user:

        return render_template("user/user.html", user = user)

    else:

        abort(404)

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

    if current_user.github_login.startswith("syntNone-") and current_user.github_login.endswith("-syntNone"):

        github_login = ""

    else:

        github_login = current_user.github_login

    form = UserProfileEditorForm(current_user.username,
                                 github_login,
                                 current_user.email)

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.github_login.data != "":

            current_user.github_login = form.github_login.data

        else:

            github_logins = [ user_data.github_login for user_data in User.query.all() ]
            condition = True

            while condition:

                tmp_github_login = "{}{}{}".format("syntNone-",
                                                   "".join(choices(ascii_letters + digits, k = 6)),
                                                   "-syntNone")

                if tmp_github_login not in github_logins:

                    condition = False

            current_user.github_login = tmp_github_login

        db.session.commit()

        flash("Ton profil a bien été mis-à-jour")

        return redirect(url_for("user.user", username = current_user.username))

    elif request.method == "GET":

        form.username.data = current_user.username
        form.github_login.data = github_login
        form.email.data = current_user.email

    return render_template("user/user_profile_editor.html",
                           title = "Modifier mon profil",
                           form = form)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
