import json
from base64 import b64encode
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse, urlencode
from pyramid.view import view_config
from pyramid.response import Response
from izinto.models import DataSource
from izinto.views import get_values, create, get, edit, filtered_list, delete

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


@view_config(route_name='data_source_views.load_data_query', permission='view')
def load_data_query(request):
    """
    Get chart data using data source query
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)

    query = {
        'q':  request.json_body.get('query'),
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
    if 'gzip' in request.accept_encoding:
        headers["Accept-Encoding"] = 'gzip'
    params = urlencode(query)
    conn.request('POST', "/query", params, headers=headers)
    remote_response = conn.getresponse()
    headers = list({
        'Content-Encoding': remote_response.headers.get('Content-Encoding'),
        'Content-Type': remote_response.headers.get('Content-Type')
    }.items())
    response = Response(remote_response.read(), status=remote_response.status, headerlist=headers,
                        content_type=remote_response.headers.get('Content-Type'))
    return response
