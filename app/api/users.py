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


    # droits seulement pour l'admin ?


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


    # droits seulement pour l'admin ?


    data = request.get_json() or {}

    if "username" not in data or "email" not in data or "password" not in data:

        return bad_request("Must include username, email and password fields")

    if User.query.filter_by(username = data["username"]).first():

        return bad_request("Please use a different username")

    if User.query.filter_by(email = data["email"]).first():

        return bad_request("Please use a different email address")

    user = User()
    user.from_dict(data, new_user = True)

    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_user", id = user.id)

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
