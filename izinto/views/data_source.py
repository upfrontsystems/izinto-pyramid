import json
from base64 import b64encode
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse, urlencode
from pyramid.view import view_config
from pyramid.response import Response
from izinto.models import DataSource
from izinto.views import get_values, create, get, edit, filtered_list, delete
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

attrs = ['name', 'type', 'url', 'username', 'password', 'database']
required_attrs = []


@view_config(route_name='data_source_views.create_data_source', renderer='json', permission='add')
def create_data_source_view(request):
    """
    Create a DataSource
    :param request:
    :return DataSource:
    """
    data = get_values(request, attrs, required_attrs)
    data_source = create(DataSource, **data)
    return data_source.as_dict()


@view_config(route_name='data_source_views.get_data_source', renderer='json', permission='view')
def get_data_source_view(request):
    """
    Get a data_source
    :param request:
    :return:
    """
    return get(request, DataSource)


@view_config(route_name='data_source_views.edit_data_source', renderer='json', permission='edit')
def edit_data_source_view(request):
    """
    Edit data_source
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(data_source, **data)

    return data_source.as_dict()


@view_config(route_name='data_source_views.list_data_sources', renderer='json', permission='view')
def list_data_sources_view(request):
    """
    List data_sources by filters
    :param request:
    :return:
    """
    return filtered_list(request, DataSource, DataSource.name)


@view_config(route_name='data_source_views.delete_data_source', renderer='json', permission='delete')
def delete_data_source_view(request):
    """
    Delete a data_source view
    :param request:
    :return:
    """
    return delete(request, DataSource)


@view_config(route_name='data_source_views.query', permission='view')
def query(request):
    """
    Get chart data using data source query
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)
    query_string = request.json_body.get('query', '')

    # query directly from database
    if not data_source.url.startswith('http'):
        return database_query(data_source, query_string)

    return http_query(request.accept_encoding, data_source, query_string)


def http_query(accept_encoding, data_source, statement):
    """ Query over http connection """
    query_params = {
        'q':  statement,
        'db': data_source.database
    }
    parse = urlparse(data_source.url)
    if parse.scheme == 'https':
        conn = HTTPSConnection(parse.netloc)
    else:
        conn = HTTPConnection(parse.netloc)

    auth = b64encode(b"%s:%s" % (data_source.username.encode('utf-8'),
                                 data_source.password.encode('utf-8'))).decode("ascii")
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "application/json",
               "Authorization": "Basic %s" % auth}
    if 'gzip' in accept_encoding:
        headers["Accept-Encoding"] = 'gzip'
    params = urlencode(query_params)
    conn.request('POST', "/query", params, headers=headers)
    remote_response = conn.getresponse()
    for header in ('Content-Encoding', 'Content-Type'):
        header_value = remote_response.headers.get('Content-Encoding')
        if header_value:
            headers[header] = header_value
    headers = list(headers.items())
    response = Response(remote_response.read(), status=remote_response.status, headerlist=headers,
                        content_type=remote_response.headers.get('Content-Type'))
    return response


def database_query(data_source, statement):
    """ Query database url directly """
    ds_session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    engine = create_engine(data_source.url)
    ds_session.configure(bind=engine)

    data = []
    with engine.connect() as con:
        result = con.execute(text(statement))
        data = json.dumps([(dict(row.items())) for row in result])
    response = Response(json_body=data)
    return response
