import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Variable
from izinto.views import get_values, create, get, edit, filtered_list, delete

attrs = ['name', 'value', 'container_id']
required_attrs = ['name', 'value', 'container_id']


@view_config(route_name='variable_views.create_variable', renderer='json', permission='add')
def create_variable_view(request):
    """
    Create a DataSource
    :param request:
    :return DataSource:
    """
    name = request.json_body.get('name')
    container_id = request.json_body.get('container_id')

    # check duplicates
    existing = session.query(Variable).filter_by(name=name, container_id=container_id).first()
    if existing:
        raise exc.HTTPBadRequest(json_body={'message': 'Variable with same id %s already exists' % name})

    data = get_values(request, attrs, required_attrs)
    data_source = create(Variable, **data)
    return data_source.as_dict()


@view_config(route_name='variable_views.get_variable', renderer='json', permission='view')
def get_variable_view(request):
    """
   Get a variable
   :param request:
   :return:
   """
    return get(request, Variable)


@view_config(route_name='variable_views.edit_variable', renderer='json', permission='edit')
def edit_variable_view(request):
    """
    Edit variable
    :param request:
    :return:
    """
    variable = get(request, Variable, as_dict=False)
    name = request.json_body.get('name')

    existing = session.query(Variable).filter_by(name=name, container_id=variable.container_id).first()
    if existing and existing.id != variable.id:
        raise exc.HTTPBadRequest(json_body={'message': 'Variable with name %s already exists' % name})

    data = get_values(request, attrs, required_attrs)
    edit(variable, **data)

    return variable.as_dict()


@view_config(route_name='variable_views.list_variables', renderer='json', permission='view')
def list_variables_view(request):
    """
    List variables by filters
    :param request:
    :return:
    """
    return filtered_list(request.params, Variable, Variable.name)


@view_config(route_name='variable_views.delete_variable', renderer='json', permission='delete')
def delete_variable_view(request):
    """
    Delete a variable view
    :param request:
    :return:
    """
    return delete(request, Variable)
