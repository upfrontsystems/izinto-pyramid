import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Variable
from izinto.services.variable import get_variable, create_variable, edit_variable, delete_variable


@view_config(route_name='variable_views.create_variable', renderer='json', permission='add')
def create_variable(request):
    data = request.json_body
    name = data.get('name')
    value = data.get('value')
    dashboard_id = data.get('dashboard_id')

    # check vital data
    if not name and value:
        raise exc.HTTPBadRequest(json_body={'message': 'Need name and value'})
    # check duplicates
    existing = get_variable(name=name, dashboard_id=dashboard_id)
    if existing:
        raise exc.HTTPBadRequest(json_body={'message': 'Variable with same id %s already exists' % name})

    variable = create_variable(name, value, dashboard_id)
    return variable.as_dict()


@view_config(route_name='variable_views.get_variable', renderer='json', permission='view')
def get_variable_view(request):
    """
   Get a variable
   :param request:
   :return:
   """
    variable_id = request.matchdict.get('id')
    if not variable_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need variable id'})
    variable = get_variable(variable_id)
    if not variable:
        raise exc.HTTPNotFound(json_body={'message': 'Variable not found'})
    variable_data = variable.as_dict()
    return variable_data


@view_config(route_name='variable_views.edit_variable', renderer='json', permission='edit')
def edit_variable(request):
    """
    Edit variable
    :param request:
    :return:
    """
    data = request.json_body
    variable_id = request.matchdict.get('id')
    name = data.get('name')
    value = data.get('value')

    # check vital data
    if not variable_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need variable id'})
    if not value:
        raise exc.HTTPBadRequest(json_body={'message': 'Need value'})
    if not name:
        raise exc.HTTPBadRequest(json_body={'message': 'Need variable id'})

    variable = get_variable(variable_id=variable_id)
    if not variable:
        raise exc.HTTPNotFound(json_body={'message': 'Variable not found'})
    existing = get_variable(name=name, dashboard_id=variable.dashboard_id)
    if existing and existing.id != variable.id:
        raise exc.HTTPBadRequest(json_body={'message': 'Variable with id %s already exists' % id})

    variable = edit_variable(variable_id, name, value)
    return variable.as_dict()


@view_config(route_name='variable_views.list_variables', renderer='json', permission='view')
def list_variables(request):
    """
    List variables by filters
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(Variable)
    for column, value in filters.items():
        query = query.filter(getattr(Variable, column) == value)

    return [variable.as_dict() for variable in query.order_by(Variable.name).all()]


@view_config(route_name='variable_views.delete_variable', renderer='json', permission='delete')
def delete_variable(request):
    """
    Delete a variable view
    :param request:
    :return:
    """
    variable_id = request.matchdict.get('id')
    variable = get_variable(variable_id)
    if not variable:
        raise exc.HTTPNotFound(json_body={'message': 'No variable found.'})

    return delete_variable(variable_id)
