import json

import pyramid.httpexceptions as exc
from pyramid.view import view_config
from sqlalchemy.exc import ProgrammingError

from izinto.models import session, Query, Dashboard, DataSource, Variable
from izinto.services.query import format_run_query
from izinto.views import get_values, create, get, edit, delete

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
    existing = session.query(Query).filter_by(name=data['name'], dashboard_id=data['dashboard_id']).first()
    if existing:
        raise exc.HTTPBadRequest(json_body={'message': 'Query %s already exists for this dashboard' % data['name']})
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

    # format query with parameters and dashboard variables
    # run http or database query
    return format_run_query(request, query.query, request.json_body, dashboard_id, query.data_source)


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
        data_source = session.query(DataSource).get(query['data_source_id'])
    except KeyError as err:
        return {'KeyError': str(err)}
    except TypeError as err:
        return {'TypeError': str(err)}
    except Exception as err:
        return {'Error': repr(err)}

    try:
        return format_run_query(request, query_string, test_data, dashboard_id, data_source)
    except KeyError as err:
        return {'KeyError': str(err)}
    except ProgrammingError as err:
        return {'SQL ProgrammingError': str(err)}
    except Exception as err:
        return {'Error': repr(err)}
