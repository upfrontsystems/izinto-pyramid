from pyramid.view import view_config
import pyramid.httpexceptions as exc

from izinto.models import DataSource
from izinto.services.query import format_run_query
from izinto.security import Administrator
from izinto.views import get_values, create, get, edit, filtered_list, delete
from izinto.views.user import get_user

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
    data['owner_id'] = request.authenticated_userid
    data_source = create(DataSource, **data)
    return data_source.as_dict()


@view_config(route_name='data_source_views.get_data_source', renderer='json', permission='view')
def get_data_source_view(request):
    """
    Get a data_source
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)
    # only admin and owner can view
    if data_source.owner_id != request.authenticated_userid:
        user = get_user(request.authenticated_userid)
        if not user.has_role(Administrator):
            raise exc.HTTPBadRequest(json_body={'message': 'Not allowed'})
    return data_source.as_dict()


@view_config(route_name='data_source_views.edit_data_source', renderer='json', permission='edit')
def edit_data_source_view(request):
    """
    Edit data_source
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)
    # only owner and admin can edit
    if data_source.owner_id != request.authenticated_userid:
        user = get_user(request.authenticated_userid)
        if not user.has_role(Administrator):
            raise exc.HTTPBadRequest(json_body={'message': 'Not allowed'})
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
    filters = request.params.copy()
    # only admin can view all data sources
    user = get_user(request.authenticated_userid)
    if not user.has_role(Administrator):
        filters['owner_id'] = request.authenticated_userid
    return filtered_list(filters, DataSource, DataSource.name)


@view_config(route_name='data_source_views.delete_data_source', renderer='json', permission='delete')
def delete_data_source_view(request):
    """
    Delete a data_source view
    :param request:
    :return:
    """
    data_source = get(request, DataSource, as_dict=False)
    # only admin and owner can delete
    if data_source.owner_id != request.authenticated_userid:
        user = get_user(request.authenticated_userid)
        if not user.has_role(Administrator):
            raise exc.HTTPBadRequest(json_body={'message': 'Not allowed'})
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

    # query formatted in front end
    # run http or database query
    return format_run_query(request, query_string, {}, None, data_source)
