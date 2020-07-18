"""
    Module to handle the errors for the "api" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


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

# ==============================================
def error_response(status_code, message = None):
    """
        Function to send a custom error response in case an API is used
        The response is composed of a status code and optionaly a message
        Those two data are input ones

        :param status_code: the status code that will be returned
        :type status_code: int

        :param message: the error message that will be returned
        :type message: None | str

        :return: the error response
        :rtype: flask.wrappers.Response
    """

    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}

    if message:

        payload["message"] = message

    response = jsonify(payload)
    response.status_code = status_code

    return response

# =======================
def bad_request(message):
    """
        Function to send a bad request response (error code 400) and an associated message (which is an input of this function)
        This function uses the error_response function to generate a custom response (notably in case an API is used)

        :param message: the error message that will be returned
        :type message: None | str

        :return: the error response
        :rtype: flask.wrappers.Response
    """

    return error_response(400, message)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
