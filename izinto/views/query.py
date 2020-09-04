from pyramid.view import view_config
from izinto.models import session, Query
from izinto.views import get_values, create, get, edit, delete
from izinto.views.data_source import database_query, http_query

attrs = ['name', 'query', 'user_id', 'data_source_id']
required_attrs = ['name', 'data_source_id']


@view_config(route_name='query_views.create_query', renderer='json', permission='add')
def create_query_view(request):
    """
    Create Query
    :param request:
    :return Query:
    """

    data = get_values(request, attrs, required_attrs)
    data['user_id'] = request.authenticated_userid
    query = create(Query, **data)

    return query.as_dict()


@view_config(route_name='query_views.get_query', renderer='json', permission='view')
def get_query_view(request):
    """
   Get a query
   :param request:
   :return:
   """
    return get(request, Query)


@view_config(route_name='query_views.edit_query', renderer='json', permission='edit')
def edit_query_view(request):
    """
    Edit query
    :param request:
    :return:
    """

    query = get(request, Query, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(query, **data)
    return query.as_dict()


@view_config(route_name='query_views.list_queries', renderer='json', permission='view')
def list_queries_view(request):
    """
    List queries
    :param request:
    :return:
    """

    filters = request.params.copy()
    if 'user_id' in filters:
        filters['user_id'] = request.authenticated_userid

    query = session.query(Query).order_by(Query.name)
    if 'user_id' in filters:
        # filter by users that can view the queries
        query = query.filter(Query.user_id == filters['user_id'])

    return [query.as_dict() for query in query.all()]


@view_config(route_name='query_views.delete_query', renderer='json', permission='delete')
def delete_query_view(request):
    """
    Delete a query
    :param request:
    :return:
    """
    return delete(request, Query)


@view_config(route_name='query_views.run_query', renderer='json', permission='view')
def run_query_view(request):
    """
    Run a query
    :param request:
    :return:
    """
    query_name = request.matchdict['name']
    user_id = request.authenticated_userid
    query = session.query(Query).filter(Query.name == query_name, Query.user_id == user_id).first()
    query_string = query.query % request.params

    # query directly from database
    if not query.data_source.url.startswith('http'):
        return database_query(query.data_source, query_string)

    return http_query(request.accept_encoding, query.data_source, query_string)
