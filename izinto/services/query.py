import decimal
import json
from base64 import b64encode
from datetime import datetime
from http.client import HTTPSConnection, HTTPConnection
import requests
from urllib.parse import urlparse, urlencode

from pyramid.response import Response
from sqlalchemy import create_engine, text
from izinto.models import session, Dashboard, Variable


def format_run_query(request, query_string, data, dashboard_id, data_source):
    """" Format query string and execute using data source """
    dashboard_variables = []
    collection_variables = []

    if dashboard_id:
        dashboard = session.query(Dashboard).get(dashboard_id)
        dashboard_variables = dashboard.variables
        if dashboard.collection_id:
            collection_variables = session.query(Variable).filter_by(container_id=dashboard.collection_id).all()

    # javascript format string
    for column, value in data.items():
        query_string = query_string.replace('${%s}' % column, value)

    # format in dashboard variables
    for variable in dashboard_variables:
        query_string = query_string.replace('${%s}' % variable.name, variable.value)

    # format in collection variables
    for variable in collection_variables:
        query_string = query_string.replace('${%s}' % variable.name, variable.value)

    # query with http request parameters
    if data_source.type == 'HTTP':
        return request_config_query(request.accept_encoding, data_source, query_string)

    # query directly over http connection
    if data_source.url.startswith('http'):
        return http_query(request.accept_encoding, data_source, query_string)
    # query directly from database
    return database_query(data_source, query_string)


def request_config_query(accept_encoding, data_source, statement):
    """ Query with request params """

    request_params = json.loads(data_source.request)
    # add default method
    if 'method' not in request_params:
        request_params['method'] = 'GET'
    # map auth from dict to tuple
    if isinstance(request_params['auth'], dict):
        request_params['auth'] = (
            request_params['auth']['username'], request_params['auth']['password'])

    # add query to params
    query_params = request_params.get('params', {})
    query_params['q'] = statement
    request_params['params'] = query_params

    remote_response = requests.request(**request_params)
    # raise any error responses
    remote_response.raise_for_status()
    # return data as json
    return remote_response.json()


def http_query(accept_encoding, data_source, statement):
    """ Query over http connection """
    query_params = {
        'q': statement,
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
    engine = create_engine(data_source.url)

    data = []
    with engine.connect() as con:
        result = con.execute(text(statement))
        data = json.dumps([(dict(row.items())) for row in result], cls=ResponseEncoder)
    response = Response(json_body=data)
    return response


class ResponseEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime):
            return str(o)
        return super(ResponseEncoder, self).default(o)
