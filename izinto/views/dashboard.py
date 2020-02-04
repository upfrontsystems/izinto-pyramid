import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Dashboard, UserDashboard
from izinto.services.user import get_user
from izinto.services.dashboard import get_dashboard, list_dashboards, paste_dashboard, build_copied_dashboard_title


@view_config(route_name='dashboard_views.create_dashboard', renderer='json', permission='add')
def create_dashboard_view(request):
    data = request.json_body
    title = data.get('title')
    description = data.get('description')
    collection_id = data.get('collection_id')
    users = data.get('users', [])

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    order = 1
    if collection_id:
        dashboards = list_dashboards(collection_id=collection_id)
        if len(dashboards):
            order = dashboards[-1].order + 1
    dashboard = Dashboard(title=title,
                          description=description,
                          collection_id=collection_id,
                          order=order)
    session.add(dashboard)
    session.flush()

    # add logged in user to dashboard
    if not [user for user in users if user['id'] == request.authenticated_userid]:
        session.add(UserDashboard(user_id=request.authenticated_userid, dashboard_id=dashboard.id))

    for user in users:
        session.add(UserDashboard(user_id=user['id'], dashboard_id=dashboard.id))

    return dashboard.as_dict()


@view_config(route_name='dashboard_views.get_dashboard', renderer='json', permission='view')
def get_dashboard_view(request):
    """
   Get a dashboard
   :param request:
   :return:
   """
    dashboard_id = request.matchdict.get('id')
    if not dashboard_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need dashboard id'})
    dashboard = get_dashboard(dashboard_id)
    if not dashboard:
        raise exc.HTTPNotFound(json_body={'message': 'Dashboard not found'})
    dashboard_data = dashboard.as_dict()
    return dashboard_data


@view_config(route_name='dashboard_views.edit_dashboard', renderer='json', permission='edit')
def edit_dashboard_view(request):
    """
    Edit dashboard
    :param request:
    :return:
    """
    data = request.json_body
    dashboard_id = request.matchdict.get('id')
    description = data.get('description')
    title = data.get('title')
    users = data.get('users', [])

    # check vital data
    if not dashboard_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need dashboard id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    dashboard = get_dashboard(dashboard_id=dashboard_id)
    if not dashboard:
        raise exc.HTTPNotFound(json_body={'message': 'Dashboard not found'})

    dashboard.description = description
    dashboard.title = title

    dashboard.users[:] = []
    for user in users:
        dashboard.users.append(get_user(user['id']))

    dashboard_data = dashboard.as_dict()
    return dashboard_data


@view_config(route_name='dashboard_views.list_dashboards', renderer='json', permission='view')
def list_dashboards_view(request):
    """
    List dashboards
    :param request:
    :return:
    """
    filters = request.params.copy()
    if 'user_id' in filters:
        filters['user_id'] = request.authenticated_userid

    return [dashboard.as_dict() for dashboard in list_dashboards(**filters)]


@view_config(route_name='dashboard_views.delete_dashboard', renderer='json', permission='delete')
def delete_dashboard_view(request):
    """
    Delete a dashboard
    :param request:
    :return:
    """
    dashboard_id = request.matchdict.get('id')
    dashboard = get_dashboard(dashboard_id)
    if not dashboard:
        raise exc.HTTPNotFound(json_body={'message': 'No dashboard found.'})

    session.query(Dashboard). \
        filter(Dashboard.id == dashboard_id). \
        delete(synchronize_session='fetch')


@view_config(route_name='dashboard_views.paste_dashboard', renderer='json', permission='add')
def paste_dashboard_view(request):
    data = request.json_body
    dashboard_id = data.get('id')
    collection_id = data.get('collection_id')

    # check vital data
    if not dashboard_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need copied dashboard'})

    dashboard = get_dashboard(dashboard_id)
    title = dashboard.title
    # make "Copy of" title
    if collection_id == dashboard.collection_id:
        title = build_copied_dashboard_title(title, collection_id)

    order = 1
    if collection_id:
        dashboards = list_dashboards(collection_id=collection_id)
        if len(dashboards):
            order = dashboards[-1].order + 1

    dashboard = paste_dashboard(dashboard_id, collection_id, title, order)
    return dashboard.as_dict()


@view_config(route_name='dashboard_views.reorder_dashboard', renderer='json', permission='edit')
def reorder_dashboard_view(request):
    data = request.json_body
    dashboard_id = request.matchdict.get('id')
    collection_id = data.get('collection_id')
    order = data.get('order')

    dashboard = get_dashboard(dashboard_id)
    if not dashboard:
        raise exc.HTTPNotFound(json_body={'message': 'No dashboard found.'})

    reorder = session.query(Dashboard).filter(Dashboard.collection_id == collection_id)

    if order > dashboard.order:
        change = -1
        reorder = reorder.filter(Dashboard.order.between(dashboard.order, order)).all()
    else:
        change = 1
        reorder = reorder.filter(Dashboard.order.between(order, dashboard.order)).all()

    for reorder_dash in reorder:
        reorder_dash.order += change
    dashboard.order = order

    return {}
