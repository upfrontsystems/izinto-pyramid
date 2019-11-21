import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Collection, Dashboard, UserDashboard, User
from izinto.services.user import get_user
from izinto.services.variable import create_variable, edit_variable, delete_variable


@view_config(route_name='dashboard_views.create_dashboard', renderer='json', permission='add')
def create_dashboard(request):
    data = request.json_body
    title = data.get('title')
    description = data.get('description')
    collection_id = data.get('collection_id')
    users = data.get('users', [])
    variables = data.get('variables', [])

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    dashboard = Dashboard(title=title,
                          description=description,
                          collection_id=collection_id)
    session.add(dashboard)
    session.flush()

    for user in users:
        session.add(UserDashboard(user_id=user['id'], dashboard_id=dashboard.id))
    for variable in variables:
        create_variable(variable['name'], variable['value'], dashboard.id)

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
    users = data.get('users', [])
    variables = data.get('variables', [])

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
    deleted = [var for var in variables if var.get('id')]
    for variable in variables:
        if variable.get('id'):
            edit_variable(variable['id'], variable['name'], variable['value'])
            deleted = [var for var in deleted if var['id'] != variable['id']]
        else:
            create_variable(variable['name'], variable['value'], dashboard.id)
    for variable in deleted:
        delete_variable(variable['id'])

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

    if 'collection_id' in filters:
        query = query.filter(Dashboard.collection_id == filters['collection_id'])
    # filter by users that can view the dashboards
    # filter by users that have access to the collection of the dashboard
    if 'user_id' in filters:
        user_query = query.join(Dashboard.users).filter(User.id == request.authenticated_userid)
        collection_query = query.join(Dashboard.collections). \
            join(Collection.users).filter(User.id == request.authenticated_userid)
        query = user_query.union(collection_query)

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
