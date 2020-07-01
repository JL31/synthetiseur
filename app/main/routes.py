"""
    Module to handle the several routes for the "main" blueprint
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request, jsonify, g, current_app
from flask_login import current_user, login_required

from app import db
from app.models import User, Article, Reference

from app.main import bp
from app.main.forms import CreateArticle, ModifyArticle, SearchForm

from datetime import datetime


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

# ===================
@bp.before_request
def before_request():
    """
        Function performed before each request to add the SearchForm instance to each page

        :return: nothing
        :rtype: None
    """

    if current_user.is_authenticated:

        g.search_form = SearchForm()

        articles = current_user.articles.all()
        g.number_of_articles = len(articles)

# ==================
@bp.route("/")
@bp.route("/index")
@login_required
def index():
    """
        View function for the index page

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    return render_template("main/index.html", title = "Index")

# ============================================================
@bp.route("/create_article", methods = ["GET", "POST"])
@login_required
def create_article():
    """
        View function for a User to create an article

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.username == "invite" and g.number_of_articles >= 5:

        return redirect(url_for("main.index"))

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        references = tmp_article.references.all()

    else:

        references = []

    form = CreateArticle()

    if form.validate_on_submit():

        tmp_article = Article.query.filter_by(title = "TMP").first()

        if not tmp_article:

            tmp_article = Article(title = "TMP",
                                  synthesis = "tmp",
                                  user_id = int(current_user.id))

            db.session.add(tmp_article)
            db.session.commit()

            tmp_article = Article.query.filter_by(title = "TMP").first()

        tmp_article.title = form.title.data
        tmp_article.synthesis = form.synthesis.data

        db.session.commit()

        flash("L'article a bien été ajouté")

        return redirect(url_for("main.user_articles_list"))

    return render_template("main/create_article.html",
                           title = "Créer un article",
                           form = form,
                           user_id = current_user.id,
                           current_article_id = -1,
                           references = references,
                           submit_button_title = "Ajouter")

# ===============================
@bp.route("/user_articles_list")
@login_required
def user_articles_list():
    """
        View function for a User to see its articles list

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    articles_list = User.query.filter_by(username = current_user.username).first().articles.all()

    return render_template("main/user_articles_list.html",
                           title = "Liste de mes articles",
                           articles_list = articles_list)

# =====================================
@bp.route("/article/<article_number>")
@login_required
def article(article_number):
    """
        View function to consult a specific article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    article = Article.query.get_or_404(int(article_number))

    article_creation_date = article.creation_date.strftime("%d/%m/%Y %H:%M:%S")
    article_update_date = article.update_date.strftime("%d/%m/%Y %H:%M:%S")

    article_creation_date_for_display = article.creation_date.strftime("%d/%m/%Y")
    article_update_date_for_display = article.update_date.strftime("%d/%m/%Y")

    dates = {"article_creation_date" : article_creation_date,
             "article_update_date" : article_update_date,
             "article_creation_date_for_display" : article_creation_date_for_display,
             "article_update_date_for_display" : article_update_date_for_display
            }

    return render_template("main/article.html", article = article, dates = dates)

# =======================================================================
@bp.route("/modify_article/<article_number>", methods = ["GET", "POST"])
@login_required
def modify_article(article_number):
    """
        View function for a User to modify an article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    article = Article.query.get_or_404(int(article_number))

    references = article.references.all()

    form = ModifyArticle()

    if form.validate_on_submit():

        article.title = form.title.data
        article.synthesis = form.synthesis.data
        article.update_date = datetime.utcnow()

        db.session.add(article)
        db.session.commit()

        flash("L'article a bien été modifié")

        return redirect(url_for("main.article", article_number = article.id))

    elif request.method == "GET":

        form.title.data = article.title
        form.synthesis.data = article.synthesis

    return render_template("main/create_article.html",
                           title = "Modifier un article",
                           form = form,
                           user_id = current_user.id,
                           current_article_id = article.id,
                           references = references,
                           submit_button_title = "Valider les modifications")

# =======================================================================
@bp.route("/delete_article/<article_number>", methods = ["GET", "POST"])
@login_required
def delete_article(article_number):
    """
        View function for a User to delete an article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if tmp_article:

        db.session.delete(tmp_article)
        db.session.commit()

    article = Article.query.get_or_404(int(article_number))

    db.session.delete(article)
    db.session.commit()

    flash("L'article a bien été suprrimé")

    return redirect(url_for("main.user_articles_list"))

# =============================================================================
@bp.route("/add_reference/<user_id>/<current_article_id>", methods = ["POST"])
@login_required
def add_reference(user_id, current_article_id):
    """
        View function to add a reference to an article (through AJAX request)

        :param user_id: the user id
        :type user_id: str

        :param current_article_id: the current article id
        :type current_article_id: str

        :return: the view to be displayed
        :rtype: str
    """

    data = {}

    if int(current_article_id) != -1:

        tmp_article = Article.query.filter_by(id = int(current_article_id)).first()

    else:

        tmp_article = Article.query.filter_by(title = "TMP").first()

        if not tmp_article:

            tmp_article = Article(title = "TMP",
                                  synthesis = "tmp",
                                  user_id = int(user_id))

            db.session.add(tmp_article)
            db.session.commit()

            tmp_article = Article.query.filter_by(title = "TMP").first()

    reference = Reference(description = request.form["references"], article = tmp_article)

    db.session.add(reference)
    db.session.commit()

    references = tmp_article.references.all()

    data["html_form"] = render_template("main/references_list.html",
                                        references = references)

    return jsonify(data)

# ====================================================================================
@bp.route("/delete_reference/<reference_id>/<current_article_id>", methods = ["GET"])
@login_required
def delete_reference(reference_id, current_article_id):
    """
        View function to delete a reference (through AJAX request)

        :param reference_id: the user id
        :type reference_id: str

        :param current_article_id: the current article id
        :type current_article_id: str

        :return: the view to be displayed
        :rtype: str
    """

    data = {}

    reference = Reference.query.filter_by(id = reference_id).first()

    db.session.delete(reference)
    db.session.commit()

    if int(current_article_id) != -1:

        tmp_article = Article.query.filter_by(id = int(current_article_id)).first()

    else:

        tmp_article = Article.query.filter_by(title = "TMP").first()

    references = tmp_article.references.all()

    data["html_form"] = render_template("main/references_list.html",
                                        references = references)

    return jsonify(data)

# ====================================================
@bp.route("/check_article_title", methods = ["POST"])
@login_required
def check_article_title():
    """
        View function to check if the current article title is already taken (through AJAX request)

        :return: the view to be displayed
        :rtype: str
    """

    data = {}

    article = Article.query.filter_by(title = request.form["title"]).first()

    if article:

        data["title_already_exists"] = True

    else:

        data["title_already_exists"] = False

    return jsonify(data)

# ===================
@bp.route("/search")
@login_required
def search():
    """
        View function to search for words among Article title and synthesis

        :return: the view to be displayed
        :rtype: str
    """

    if not g.search_form.validate():

        return redirect(url_for("main.user_articles_list"))

    page = request.args.get("page", 1, type = int)

    articles, total = Article.search(g.search_form.q.data,
                                     page,
                                     current_app.config["SEARCH_ARTICLES_PER_PAGE"])


    if total > page * current_app.config["SEARCH_ARTICLES_PER_PAGE"]:

        next_url = url_for("main.search", q = g.search_form.q.data, page = page + 1)

    else:

        next_url = None

    if page > 1:

        prev_url = url_for("main.search", q = g.search_form.q.data, page = page - 1)

    else:

        prev_url = None

    return render_template("main/search.html",
                           title = "Résultat de la recherche",
                           articles = articles,
                           next_url = next_url,
                           prev_url = prev_url)

# ====================================================================================================
@bp.route("/article_deletion_confirmation_modal_content_loading/<article_number>", methods = ["GET"])
@login_required
def article_deletion_confirmation_modal_content_loading(article_number):
    """
        View function to search for words among Article title and synthesis

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    # fake form just to enable having the CSRF token value in the bootstrap modal form (using "form.hidden_tag()") 
    form = ModifyArticle()

    data = {}

    data["html_form"] = render_template("main/modal_article_deletion.html",
                                        article_number = article_number,
                                        form = form)

    return jsonify(data)


# ==================================================================================================
#
# USE
#
# ==================================================================================================
