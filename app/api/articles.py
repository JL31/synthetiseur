"""
    Module to handle the several api for the articles
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

from app.models import User, Article, Reference


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

# ================================================
@bp.route("/articles/<int:id>", methods = ["GET"])
@token_auth.login_required
def get_articles(id):
    """
        API that enables to get the articles list for a given user
        (identified through its id)

        :param id: the cuser identifier
        :type id: int

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    if token_auth.current_user().id != id:

        abort(403)

    user_articles = User.query.get_or_404(id).articles

    data_articles = [ article.to_dict() for article in user_articles ]

    data = {}
    data["items"] = data_articles
    data["_meta"] = {"total_items": len(data_articles)}

    return jsonify(data)

# =================================================
@bp.route("/articles/<int:id>", methods = ["POST"])
@token_auth.login_required
def create_article(id):
    """
        API that enables to create an article for a given user
        (identified through its id)

        :param id: the cuser identifier
        :type id: int

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    if token_auth.current_user().id != id:

        abort(403)

    data = request.get_json() or {}

    if "title" not in data or "synthesis" not in data:

        return bad_request("Must include title and synthesis fields")

    if Article.query.filter_by(title = data["title"]).first():

        return bad_request("Please use a different title")

    article = Article(user_id = id)
    article.from_dict(data, new_article = True)

    db.session.add(article)
    db.session.commit()

    if "references" in data:

        try:

            references_data = data["references"].split(";")
            references_data = [ item.strip() for item in references_data ]

        except AttributeError:

            return bad_request("Error in the references definition: must be a sequence of string separated with comas")

        for reference in references_data:

            new_reference = Reference(description = reference, article = article)
            db.session.add(new_reference)
            db.session.commit()

    response = jsonify(article.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_articles", id = id)

    return response

# ======================================================================
@bp.route("/articles/<int:user_id>/<int:article_id>", methods = ["PUT"])
@token_auth.login_required
def update_article(user_id, article_id):
    """
        API that enables to modify the current article for a given user
        (identified through its id)

        :param user_id: the current user identifier
        :type user_id: int

        :param article_id: the current article identifier
        :type article_id: int

        :return: the Response object containing the data (in JSON format)
        :rtype: flask.wrappers.Response
    """

    if token_auth.current_user().id != user_id:

        abort(403)

    article = Article.query.get_or_404(article_id)
    article_references = article.references
    article_references = [ item.description for item in article_references ]

    data = request.get_json() or {}

    if "title" in data and data["title"] == article.title and Article.query.filter_by(title = data["title"]).first():

        return bad_request("Please use a different title")

    article.from_dict(data, new_article = False)
    db.session.commit()

    if "references" in data:

        try:

            references_data = data["references"].split(";")
            references_data = [ item.strip() for item in references_data ]

        except AttributeError:

            return bad_request("Error in the references definition: must be a sequence of string separated with comas")

        for reference in references_data:

            if reference not in article_references:

                new_reference = Reference(description = reference, article = article)
                db.session.add(new_reference)
                db.session.commit()

    response = jsonify(article.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_articles", id = user_id)

    return response


# ==================================================================================================
#
# USE
#
# ==================================================================================================
