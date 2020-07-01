"""
    Module to handle searching among articles for the application (using "Elasticsearch" module)
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import current_app


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

# =============================
def add_to_index(index, model):
    """
        Function to add entries (model fields values) to an index

        :param index: the index name
        :type index: str

        :param model: SQLAlchemy model
        :type model: app.models

        :return: Nothing
        :rtype: None
    """

    if not current_app.elasticsearch:

        return None

    payload = {}

    for field in model.__searchable__:

        payload[field] = getattr(model, field)

    current_app.elasticsearch.index(index = index, id = model.id, body = payload)

# ==================================
def remove_from_index(index, model):
    """
        Function to remove entries (model fields values) from an index

        :param index: the index name
        :type index: str

        :param model: SQLAlchemy model
        :type model: app.models

        :return: Nothing
        :rtype: None
    """

    if not current_app.elasticsearch:

        return None

    current_app.elasticsearch.delete(index = index, id = model.id)

# ============================================
def query_index(index, query, page, per_page):
    """
        Function to query an index

        :param index: the index name
        :type index: str
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        :param query: the searched text 
        :type query: str

        :param page: page number of the ElasticSearch result query
        :type page: int

        :param per_page: number of results per page of the ElasticSearch result query
        :type per_page: int

        :return:
        :rtype: tuple(list, int)

        Examples:

        Looking for words 'one two three four five' in the 'posts' index.
        First  displaying results for page 1 with 100 items per page.
        Second displaying results for page 1 with 3 items per page.
        Third  displaying results for page 2 with 3 items per page.
        Fourth displaying results for page 3 with 3 items per page.

        >>> query_index('posts', 'one two three four five', 1, 100)
        ([15, 13, 12, 4, 11, 8, 14], 7)
        
        >>> query_index('posts', 'one two three four five', 1, 3)
        ([15, 13, 12], 7)
        
        >>> query_index('posts', 'one two three four five', 2, 3)
        ([4, 11, 8], 7)
        
        >>> query_index('posts', 'one two three four five', 3, 3)
        ([14], 7)
    """

    if not current_app.elasticsearch:

        return ([], 0)

    search = current_app.elasticsearch.search(index = index,
                                              body = {'query': {'multi_match': {'query': query, 
                                                                                'fields': ['*']
                                                                                }
                                                                },
                                                      'from': (page - 1) * per_page,
                                                      'size': per_page
                                                     })

    ids = [ int(hit['_id']) for hit in search['hits']['hits'] ]

    return (ids, search['hits']['total']['value'])


# ==================================================================================================
#
# USE
#
# ==================================================================================================
