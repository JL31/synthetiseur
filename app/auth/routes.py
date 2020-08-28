"""
    Module to handle the several routes for the "auth" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user

from werkzeug.urls import url_parse

from app import db

from app.models import User, Article

from app.auth import bp
from app.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email

from string import ascii_uppercase, digits
from random import choices
from rauth import OAuth2Service


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

# ========================
class OAuthSignIn(object):
    """
        Class to handle the sign in throught OAuth protocol
        This class is an abstraction that enables to handle any kind of providers (ex.: GitHub, Gmail...)
    """

    providers = None

    # ================================
    def __init__(self, provider_name):
        """
            Class constructor

            :param provider_name: the name of the provider
            :type provider_name: str
        """

        self.provider_name = provider_name

        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]

        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    # ==================
    def authorize(self):
        """
            Method to enable the application to redirect to the
            provider's website to let the user authenticate there
        """

        pass

    # ==================
    def callback(self):
        """
            Method to redirect the user back to the application
            once the authentication is completed
        """

        pass

    # =========================
    def get_callback_url(self):
        """
            Method to generate the URL for the callback depending on the provider

            :return: the URL for the OAuth callback
            :rtype: str
        """

        return url_for("auth.oauth_callback",
                       provider = self.provider_name,
                       _external = True)

    # ====================================
    @classmethod
    def get_provider(self, provider_name):
        """
            Class method to get the selected provider class instance

            :param provider_name: the name of the provider
            :type provider_name: str

            :return: the selected provider class instance
            :rtype: GitHubSignIn
        """

        if self.providers is None:

            self.providers = {}

            for provider_class in self.__subclasses__():

                provider = provider_class()
                self.providers[provider.provider_name] = provider

        return self.providers[provider_name]

# ==============================
class GitHubSignIn(OAuthSignIn):
    """
        Class to handle the sign in through GitHub account
    """

    # =================
    def __init__(self):
        """
            Class constructor
        """
        
        super(GitHubSignIn, self).__init__("github")

        oauth2service_data = {
                              "name" : "github",
                              "client_id" : self.consumer_id,
                              "client_secret" : self.consumer_secret,
                              "authorize_url" : "https://github.com/login/oauth/authorize",
                              "access_token_url" : "https://github.com/login/oauth/access_token",
                              "base_url" : "https://api.github.com/user"
                             }

        self.service = OAuth2Service(**oauth2service_data)

    # ==================
    def authorize(self):
        """
            Overriding of the "authorize" method of the parent class

            This method to enable the application to redirect to the 
            provider's website to let the user authenticate there

            :return: the response
            :rtype: werkzeug.wrappers.response.Response
        """

        request_data = {
                        "client_id" : self.service.client_id,
                        "scope" : "user",
                        "redirect_uri" : self.get_callback_url()
                       }

        return redirect(self.service.get_authorize_url(**request_data))

    # ================
    def callback(self):
        """
            Overriding of the "callback" method of the parent class

            This method redirects the user back to the
            application once the authentication is completed

            :return: the GitHub login
            :rtype: None | str
        """

        if "code" not in request.args:

            return None

        get_auth_session_data = {
                                 "data" : {
                                           "code": request.args["code"],
                                           "grant_type": "authorization_code",
                                           "redirect_uri": self.get_callback_url()
                                          }
                                }

        oauth_session = self.service.get_auth_session(**get_auth_session_data)

        github_user_data = oauth_session.get("user").json()

        return github_user_data.get("login")


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

    current_user_username = current_user.username
    current_user_is_guest = current_user.is_guest

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    logout_user()

    if current_user_is_guest:

        guest_user = User.query.filter_by(username = current_user_username).first()
        db.session.delete(guest_user)
        db.session.commit()    

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

# =================================================
@bp.route("/guest_test_request", methods = ["GET"])
def guest_test_request():
    """
        View function for a guest to ask for a test session

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("main.index"))

    return render_template("auth/guest_test_request.html", title = "Faire un essai ?")

# ==================================================
@bp.route("/start_guest_session", methods = ["GET"])
def start_guest_session():
    """
        View function for a guest to start a session (limited in time duration)

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("main.index"))

    users = User.query.all()
    usernames_list = [ user.username for user in users ]

    condition = True

    while condition:

        guest_username = "".join(choices(ascii_uppercase + digits, k = 10))

        if guest_username not in usernames_list:

            condition  = False

    guest_user = User(username = guest_username,
                      email = "dummy data",
                      is_guest = True)

    db.session.add(guest_user)
    db.session.commit()

    login_user(guest_user)

    return redirect(url_for("main.index"))

# ================================
@bp.route("/authorize/<provider>")
def oauth_authorize(provider):
    """
        View function to initiate an OAuth authentication

        :param provider: the provider's name
        :type provider: str

        :return: the response
        :rtype: werkzeug.wrappers.response.Response
    """

    if not current_user.is_anonymous:

        return redirect(url_for("main.index"))

    oauth = OAuthSignIn.get_provider(provider)

    return oauth.authorize()

# ===============================
@bp.route("/callback/<provider>")
def oauth_callback(provider):
    """
        View function to login a user if already connected to GitHub website

        :param provider: the provider's name
        :type provider: str

        :return: the view to be displayed
        :rtype: str
    """

    if not current_user.is_anonymous:

        return redirect(url_for("main.index"))

    oauth = OAuthSignIn.get_provider(provider)

    github_login = oauth.callback()

    if github_login is None:

        flash("Authentication failed")
        return redirect(url_for("main.index"))

    user = User.query.filter_by(github_login = github_login).first()

    login_user(user, True)

    return redirect(url_for("main.index"))


# ==================================================================================================
#
# USE
#
# ==================================================================================================
