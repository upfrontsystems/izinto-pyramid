import pyramid.httpexceptions as exc
from pyramid.view import view_config
from sqlalchemy import func

from izinto.models import session, Script
from izinto.views import reorder, delete, filtered_list, get


@view_config(route_name='script_views.create_script', renderer='json', permission='add')
def create_script_view(request):
    data = request.json_body
    title = data.get('title')
    dashboard_id = data.get('dashboard_id')
    index = data.get('index', None)
    content = data.get('content')

    if index is None:
        result = session.query(func.count(Script.id)).filter(Script.dashboard_id == dashboard_id).first()
        index = result[0]

    # check required data
    if not (title and content):
        raise exc.HTTPBadRequest(json_body={'message': 'Need title and script content'})

    script = Script(title=title,
                    dashboard_id=dashboard_id,
                    index=index,
                    content=content)
    session.add(script)
    session.flush()

    return script.as_dict()


@view_config(route_name='script_views.edit_script', renderer='json', permission='edit')
def edit_script_view(request):
    """
    Edit script
    :param request:
    :return:
    """
    data = request.json_body
    script_id = request.matchdict.get('id')
    title = data.get('title')
    content = data.get('content')

    # check vital data
    if not script_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need script id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})
    if not content:
        raise exc.HTTPBadRequest(json_body={'message': 'Need script content'})

    script = session.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise exc.HTTPNotFound(json_body={'message': 'Script not found'})

    script.title = title
    script.content = content

    return script.as_dict()


@view_config(route_name='script_views.reorder_script', renderer='json', permission='edit')
def reorder_script_view(request):
    data = request.json_body
    script_id = request.matchdict.get('id', None)
    index = data.get('index', None)
    if script_id is None:
        raise exc.HTTPBadRequest(json_body={'message': 'Need record id'})
    if index is None:
        raise exc.HTTPBadRequest(json_body={'message': 'index of new position not found'})
    script = session.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise exc.HTTPNotFound(json_body={'message': 'Script not found'})
    dashboard_scripts = session.query(Script).filter(Script.dashboard_id == script.dashboard_id)
    reorder(index, script, Script, dashboard_scripts)
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
