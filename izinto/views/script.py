import pyramid.httpexceptions as exc
from pyramid.view import view_config
from sqlalchemy import func

from izinto.models import session, Script
from izinto.views import create, edit, reorder, delete, filtered_list, get, get_values


@view_config(route_name='script_views.create_script', renderer='json', permission='add')
def create_script_view(request):
    """
    Create Script
    :param request:
    :return:
    """
    attrs = required_attrs = ['dashboard_id', 'title', 'content']
    data = get_values(request, attrs, required_attrs)

    if data.get('index') is None:
        result = session.query(func.count(Script.id)).filter(Script.dashboard_id == data.get('dashboard_id')).first()
        data['index'] = result[0]

    script = create(Script, **data)

    return script.as_dict()


@view_config(route_name='script_views.edit_script', renderer='json', permission='edit')
def edit_script_view(request):
    """
    Edit Script
    :param request:
    :return:
    """
    script = get(request, Script, as_dict=False)
    attrs = required_attrs = ['title', 'content']
    data = get_values(request, attrs, required_attrs)
    edit(script, **data)

    return script.as_dict()


@view_config(route_name='script_views.reorder_script', renderer='json', permission='edit')
def reorder_script_view(request):
    script = get(request, Script, as_dict=False)
    data = get_values(request, ['index'], ['index'])
    dashboard_scripts = session.query(Script).filter(Script.dashboard_id == script.dashboard_id)
    reorder(data.get('index'), script, Script, dashboard_scripts)
    return {}


@view_config(route_name='script_views.get_script', renderer='json', permission='view')
def get_script_view(request):
    """ Get a script """
    return get(request, Script)


@view_config(route_name='script_views.list_scripts', renderer='json', permission='view')
def list_scripts_view(request):
    """ List scripts """
    return filtered_list(request, Script, Script.index)


@view_config(route_name='script_views.delete_script', renderer='json', permission='delete')
def delete_script_view(request):
    """ Delete a script """
    return delete(request, Script)
