import json
from pyramid.view import view_config
from sqlalchemy.exc import ProgrammingError
import pyramid.httpexceptions as exc
from izinto.models import session, Query, Dashboard, DataSource
from izinto.views import get_values, create, get, edit, delete
from izinto.views.data_source import database_query, http_query

attrs = ['name', 'query', 'dashboard_id', 'data_source_id']
required_attrs = ['name', 'data_source_id', 'dashboard_id']


@view_config(route_name='query_views.create_query', renderer='json', permission='add')
def create_query_view(request):
    """
    Create Query
    :param request:
    :return Query:
    """

    data = get_values(request, attrs, required_attrs)
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
    if 'dashboard_id' in request.matchdict:
        filters['dashboard_id'] = request.matchdict['dashboard_id']

    query = session.query(Query).order_by(Query.name)
    if 'dashboard_id' in filters:
        query = query.filter(Query.dashboard_id == filters['dashboard_id'])

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
    dashboard_id = request.matchdict['dashboard_id']
    query = session.query(Query).filter(Query.name == query_name, Query.dashboard_id == dashboard_id).first()
    if not query:
        raise exc.HTTPNotFound(json_body={'message': 'Query %s not found' % query_name})

    dashboard = session.query(Dashboard).get(dashboard_id)
    return format_run_query(request, query.query, request.json_body, dashboard, query.data_source)


@view_config(route_name='query_views.test_query', renderer='json', permission='view')
def test_query_view(request):
    """
    Run a query with test values
    :param request:
    :return:
    """

    try:
        query = request.json_body['query']
        query_string = query['query']
        test_data = json.loads(request.json_body['data'])
        dashboard_id = request.matchdict['dashboard_id']
        dashboard = session.query(Dashboard).get(dashboard_id)
        data_source = session.query(DataSource).get(query['data_source_id'])
    except KeyError as err:
        return {'KeyError': str(err)}
    except TypeError as err:
        return {'TypeError': str(err)}
    except Exception as err:
        return {'Error': repr(err)}

    try:
        return format_run_query(request, query_string, test_data, dashboard, data_source)
    except KeyError as err:
        return {'KeyError': str(err)}
    except ProgrammingError as err:
        return {'SQL ProgrammingError': str(err)}
    except Exception as err:
        return {'Error': repr(err)}


def format_run_query(request, query_string, data, dashboard, data_source):
    """" Format query string and return result """
    # javascript format string
    for column, value in data.items():
        query_string = query_string.replace('${%s}' % column, value)

    # format in dashboard variables
    for variable in dashboard.variables:
        query_string = query_string.replace('${%s}' % variable.name, variable.value)

    # query directly from database
    if data_source.url.startswith('http'):
        return http_query(request.accept_encoding, data_source, query_string)

    return database_query(data_source, query_string)
