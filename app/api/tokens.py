"""
    Module to handle the tokens for the "api" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


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

# ======================================
@bp.route("/tokens", methods = ["POST"])
@basic_auth.login_required
def get_token():
    """
        Method to get a token during API authentication process

        :return: .
        :rtype: .
    """

    token = basic_auth.current_user().get_token()

    db.session.commit()

    return jsonify({"token": token})

# ========================================
@bp.route("/tokens", methods = ["DELETE"])
@token_auth.login_required
def revoke_token():
    """
        Method to revoke a token granted during API authentication process

        :return: the response
        :rtype: werkzeug.wrappers.response.Response
    """

    token_auth.current_user().revoke_token()

    db.session.commit()

    return "", 204


# ==================================================================================================
#
# USE
#
# ==================================================================================================
