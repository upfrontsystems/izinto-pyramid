import json
from base64 import b64encode
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse
import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, DataSource
from izinto.services.data_source import get_data_source


@view_config(route_name='data_source_views.create_data_source', renderer='json', permission='add')
def create_data_source_view(request):
    data = request.json_body
    name = data.get('name')
    typ = data.get('type')
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    database = data.get('database')

    data_source = DataSource(name=name,
                             type=typ,
                             url=url,
                             username=username,
                             password=password,
                             database=database)
    session.add(data_source)
    session.flush()

    return data_source.as_dict()


@view_config(route_name='data_source_views.get_data_source', renderer='json', permission='view')
def get_data_source_view(request):
    """
    Get a data_source
    :param request:
    :return:
    """
    data_source_id = request.matchdict.get('id')
    if not data_source_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need data source id'})
    data_source = get_data_source(data_source_id)
    if not data_source:
        raise exc.HTTPNotFound(json_body={'message': 'Data Source not found'})
    data_source_data = data_source.as_dict()
    return data_source_data


@view_config(route_name='data_source_views.edit_data_source', renderer='json', permission='edit')
def edit_data_source_view(request):
    """
    Edit data_source
    :param request:
    :return:
    """
    data = request.json_body
    data_source_id = request.matchdict.get('id')
    name = data.get('name')
    typ = data.get('type')
    url = data.get('url', 0)
    username = data.get('username', '')
    password = data.get('password', '')
    database = data.get('database', '')

    # check vital data
    if not data_source_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need data source id'})

    data_source = get_data_source(data_source_id)
    if not data_source:
        raise exc.HTTPNotFound(json_body={'message': 'Data Source not found'})

    data_source.name = name
    data_source.type = typ
    data_source.url = url
    data_source.username = username
    data_source.password = password
    data_source.database = database

    return data_source.as_dict()


@view_config(route_name='data_source_views.list_data_sources', renderer='json', permission='view')
def list_data_sources_view(request):
    """
    List data_sources by filters
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(DataSource)
    for column, value in filters.items():
        query = query.filter(getattr(DataSource, column) == value)

    return [data_source.as_dict() for data_source in query.order_by(DataSource.name).all()]


@view_config(route_name='data_source_views.delete_data_source', renderer='json', permission='delete')
def delete_data_source_view(request):
    """
    Delete a data_source view
    :param request:
    :return:
    """
    data_source_id = request.matchdict.get('id')
    data_source = get_data_source(data_source_id)
    if not data_source:
        raise exc.HTTPNotFound(json_body={'message': 'No data source found.'})

    return session.query(DataSource). \
        filter(DataSource.id == data_source_id). \
        delete(synchronize_session='fetch')


@view_config(route_name='data_source_views.load_data_query', renderer='json', permission='view')
def load_data_query(request):
    """
    Get chart data using data source query
    :param request:
    :return:
    """

    data_source_id = request.matchdict.get('id')
    data_source = get_data_source(data_source_id)
    if not data_source:
        raise exc.HTTPNotFound(json_body={'message': 'No data source found.'})

    query = request.params.get('query')
    parse = urlparse(data_source.url)
    if parse.scheme == 'https':
        conn = HTTPSConnection(parse.netloc)
    else:
        conn = HTTPConnection(parse.netloc)

    auth = b64encode(b"%s:%s" % (data_source.username.encode('utf-8'),
                                 data_source.password.encode('utf-8'))).decode("ascii")
    headers = {'Content-type': 'application/json',
               'Authorization': 'Basic %s' % auth}
    conn.request('GET', query, headers=headers)
    response = conn.getresponse()
    data = response.read()
    data = json.loads(data.decode("utf-8"))

    return data
