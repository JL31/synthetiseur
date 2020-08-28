"""
    Module to handle the several api for the users
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import abort, jsonify, request, url_for

from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

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

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# =============================================
@bp.route("/users/<int:id>", methods = ["GET"])
@token_auth.login_required
def get_user(id):
    """
        API that returns the data for a specific user identified through its id

        :param id: the current user identifier
        :type id: int

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    if token_auth.current_user().id != id:

        abort(403)

    return jsonify(User.query.get_or_404(id).to_dict())

# ====================================
@bp.route("/users", methods = ["GET"])
@token_auth.login_required
def get_users():
    """
        API that returns the data for a all users

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    users_list = User.query.all()

    users_data = [ user.to_dict() for user in users_list ]

    data = {}
    data["items"] = users_data
    data["_meta"] = {"total_items": len(users_list)}

    return jsonify(data)

# =====================================
@bp.route("/users", methods = ["POST"])
def create_user():
    """
        API that creates a user

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    # request data retrieval
    data = request.get_json() or {}

    # test if username, email and password are in the request data (they must be)
    if "username" not in data or "email" not in data or "password" not in data:

        return bad_request("Must include username, email and password fields")

    # github login case : if in request data must be different than the ones already chosen
    if "github_login" in data:

        if User.query.filter_by(github_login = data["github_login"]).first():

            return bad_request("Please use a different username")

    # github login case : if no GitHub login filled-in then a random one is chosen
    else:

        github_logins = [ user_data.github_login for user_data in User.query.all() ]
        condition = True

        while condition:

            tmp_github_login = "{}{}{}".format("syntNone-",
                                               "".join(choices(ascii_letters + digits, k = 6)),
                                               "-syntNone")

            if tmp_github_login not in github_logins:

                condition = False

        data["github_login"] = tmp_github_login

    # test if chosen username is not already picked
    if User.query.filter_by(username = data["username"]).first():

        return bad_request("Please use a different username")

    # test if chosen email is not already picked
    if User.query.filter_by(email = data["email"]).first():

        return bad_request("Please use a different email address")

    # user creation
    user = User()
    user.from_dict(data, new_user = True)

    # user addition into DB
    db.session.add(user)
    db.session.commit()

    # response creation
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_user", id = user.id)

    # function return
    return response

# =============================================
@bp.route("/users/<int:id>", methods = ["PUT"])
@token_auth.login_required
def update_user(id):
    """
        API that updates a specific user data. The user is identified through its id.

        :param id: the current user identifier
        :type id: int

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    if token_auth.current_user().id != id:

        abort(403)

    user = User.query.get_or_404(id)
    data = request.get_json() or {}

    if "username" in data and data["username"] == user.username and User.query.filter_by(username = data["username"]).first():

        return bad_request("Please use a different username")

    if "github_login" in data and data["github_login"] == user.github_login and User.query.filter_by(github_login = data["github_login"]).first():

        return bad_request("Please use a different GitHub login")

    if "email" in data and data["email"] == user.email and User.query.filter_by(email = data["email"]).first():

        return bad_request("please use a different email address")

    user.from_dict(data, new_user = False)
    db.session.commit()

    return jsonify(user.to_dict())


# ==================================================================================================
#
# USE
#
# ==================================================================================================
