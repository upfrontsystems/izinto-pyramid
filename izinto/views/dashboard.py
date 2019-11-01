import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Dashboard


@view_config(route_name='dashboard_views.create_dashboard', renderer='json', permission='add')
def create_dashboard(request):
    data = request.json_body
    title = data.get('title')
    description = data.get('description')
    user_id = data.get('user_id')

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})
    if not user_id:
        user_id = request.authenticated_userid

    dashboard = Dashboard(title=title,
                  description=description,
                  user_id=user_id)
    session.add(dashboard)
    session.flush()

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


def get_dashboard(dashboard_id=None):
    """
    Get a dashboard
    :param dashboard_id:
    :return:
    """

    query = session.query(Dashboard)

    if dashboard_id:
        query = query.filter(Dashboard.id == dashboard_id)

    return query.first()


@view_config(route_name='dashboard_views.edit_dashboard', renderer='json', permission='edit')
def edit_dashboard(request):
    """
    Edit dashboard
    :param request:
    :return:
    """
    data = request.json_body
    dashboard_id = request.matchdict.get('id')
    description = data.get('description')
    title = data.get('title')
    user_id = data.get('user_id')

    # check vital data
    if not dashboard_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need dashboard id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    dashboard = get_dashboard(dashboard_id=dashboard_id)
    if not dashboard:
        raise exc.HTTPNotFound(json_body={'message': 'Dashboard not found'})

    dashboard.user_id = user_id
    dashboard.description = description
    dashboard.title = title

    dashboard_data = dashboard.as_dict()
    return dashboard_data


@view_config(route_name='dashboard_views.list_dashboards', renderer='json', permission='view')
def list_dashboards(request):
    """
    List dashboards
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(Dashboard)

    return [dashboard.as_dict() for dashboard in query.order_by(Dashboard.title).all()]


@view_config(route_name='dashboard_views.delete_dashboard', renderer='json', permission='delete')
def delete_dashboard(request):
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
