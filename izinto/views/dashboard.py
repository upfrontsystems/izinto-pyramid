from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func
from izinto.models import session, Dashboard, UserDashboard, Variable, Chart, ChartGroupBy, SingleStat, User, \
    DashboardView, Query, Role, UserCollection
from izinto.security import Administrator
from izinto.views import get_values, create, get, edit, filtered_list, delete, paste, reorder, get_user
from izinto.views.chart import attrs as chart_attrs
from izinto.views.query import attrs as query_attrs

attrs = ['title', 'description', 'collection_id', 'type', 'content', 'date_hidden', 'image']
required_attrs = ['title']


@view_config(route_name='dashboard_views.create_dashboard', renderer='json', permission='add')
def create_dashboard_view(request):
    """
    Create Dashboard
    :param request:
    :return Dashboard:
    """

    data = get_values(request, attrs, required_attrs)
    collection_id = request.json_body.get('collection_id')

    if data.get('index') is None and collection_id:
        result = session.query(func.count(Dashboard.id)).filter(Dashboard.collection_id == collection_id).first()
        data['index'] = result[0]

    dashboard = create(Dashboard, **data)

    # when creating a dashboard in a collection copy the user access from the collection
    user_access = []
    if collection_id:
        user_access = session.query(UserCollection).filter(UserCollection.collection_id == collection_id).all()
        for access in user_access:
            create(UserDashboard, user_id=access.user_id, dashboard_id=dashboard.id, role_id=access.role_id)

    if not [access for access in user_access if access.user_id == request.authenticated_userid]:
        # add logged in user to dashboard with admin role
        admin_role = session.query(Role).filter_by(name=Administrator).first()
        create(UserDashboard, user_id=request.authenticated_userid, dashboard_id=dashboard.id, role_id=admin_role.id)

    return dashboard.as_dict()


@view_config(route_name='dashboard_views.get_dashboard', renderer='json', permission='view')
def get_dashboard_view(request):
    """
   Get a dashboard
   :param request:
   :return:
   """
    return get(request, Dashboard)


@view_config(route_name='dashboard_views.edit_dashboard', renderer='json', permission='edit')
def edit_dashboard_view(request):
    """
    Edit dashboard
    :param request:
    :return:
    """

    dashboard = get(request, Dashboard, as_dict=False)

    data = get_values(request, attrs, required_attrs)
    edit(dashboard, **data)

    return dashboard.as_dict()


@view_config(route_name='dashboard_views.list_dashboards', renderer='json', permission='view')
def list_dashboards_view(request):
    """
    List dashboards
    :param request:
    :return:
    """

    filters = request.params.copy()
    query = session.query(Dashboard)

    # filter dashboards either by collection or users
    if 'collection_id' in filters:
        # filter for dashboards in a collection, and dashboard not in a collection
        if filters['collection_id']:
            query = query.filter(Dashboard.collection_id == filters['collection_id']).order_by(Dashboard.index)
        else:
            query = query.filter(Dashboard.collection_id == None).order_by(Dashboard.index)

    user = get_user(request.authenticated_userid)
    if not user.has_role(Administrator) or filters.get('user_id'):
        # filter by users that can view the dashboards
        query = query.join(Dashboard.users).filter(User.id == user.id).order_by(Dashboard.index)

    return [dashboard.as_dict() for dashboard in query.all()]


@view_config(route_name='dashboard_views.delete_dashboard', renderer='json', permission='delete')
def delete_dashboard_view(request):
    """
    Delete a dashboard
    :param request:
    :return:
    """
    return delete(request, Dashboard)


@view_config(route_name='dashboard_views.paste_dashboard', renderer='json', permission='add')
def paste_dashboard_view(request):
    """
    Paste a dashboard view
    :param request:
    :return Dashboard:
    """

    dashboard = get(request, Dashboard, as_dict=False)
    data = {attr: getattr(dashboard, attr) for attr in attrs}

    pasted_dashboard = paste(request, Dashboard, data, 'collection_id', 'title')

    _paste_dashboard_relationships(dashboard, pasted_dashboard)

    return pasted_dashboard.as_dict()


def _paste_dashboard_relationships(dashboard, pasted_dashboard):
    """ Copy all relationships when pasting new dashboard """
    # copy list of users
    user_access = session.query(UserDashboard).filter(UserDashboard.dashboard_id == dashboard.id).all()
    for access in user_access:
        create(UserDashboard, user_id=access.user_id, dashboard_id=pasted_dashboard.id, role_id=access.role_id)

    # copy list of variables
    for variable in dashboard.variables:
        create(Variable, name=variable.name, value=variable.value, dashboard_id=pasted_dashboard.id)

    # copy charts
    for chart in session.query(Chart).filter(Chart.dashboard_id == dashboard.id).all():
        data = {attr: getattr(chart, attr) for attr in chart_attrs}
        data['dashboard_id'] = pasted_dashboard.id
        data['index'] = chart.index
        pasted_chart = create(Chart, **data)

        for group in chart.group_by:
            create(ChartGroupBy, chart_id=pasted_chart.id, dashboard_view_id=group.dashboard_view_id, value=group.value)

    # copy single stats
    for stat in session.query(SingleStat).filter(SingleStat.dashboard_id == dashboard.id).all():
        create(SingleStat, title=stat.title, query=stat.query, decimals=stat.decimals, format=stat.format,
               thresholds=stat.thresholds, colors=stat.colors, dashboard_id=pasted_dashboard.id,
               data_source_id=stat.data_source_id)

    # copy queries
    for query in session.query(Query).filter(Query.dashboard_id == dashboard.id).all():
        data = {attr: getattr(query, attr) for attr in query_attrs}
        data['dashboard_id'] = pasted_dashboard.id
        create(Query, **data)


@view_config(route_name='dashboard_views.reorder_dashboard', renderer='json', permission='edit')
def reorder_dashboard_view(request):
    """
    Reorder a dashboard in a list view
    :param request:
    :return Dashboard:
    """

    dashboard = get(request, Dashboard, as_dict=False)
    data = get_values(request, ['index'], ['index'])
    collection_dashboards = session.query(Dashboard).filter(Dashboard.collection_id == dashboard.collection_id)
    reorder(data.get('index'), dashboard, Dashboard, collection_dashboards)
    return {}


@view_config(route_name='dashboard_views.list_dashboard_view_items', renderer='json', permission='edit')
def list_dashboard_view_items(request):
    """
    List DashboardView by filters
    :param request:
    :return DashboardView list:
    """

    return filtered_list(request, DashboardView, DashboardView.id)


@view_config(route_name='dashboard_views.get_content_view')
def get_content_view(request):
    """ Return dashboard content """
    dashboard = get(request, Dashboard, as_dict=False)
    return Response(dashboard.content)


@view_config(route_name='dashboard_views.edit_content_view')
def edit_content_view(request):
    """ Return dashboard content """
    dashboard = get(request, Dashboard, as_dict=False)
    content = request.json_body.get('content', '')
    edit(dashboard, content=content)
    return Response(dashboard.content)


@view_config(route_name='dashboard_views.list_user_access', renderer='json', permission='view')
def list_dashboards_user_access_view(request):
    """
    List user dashboards mapping for this dashboard with roles
    :param request:
    :return:
    """

    dashboard_id = request.matchdict['id']
    user_access = session.query(UserDashboard).filter(UserDashboard.dashboard_id == dashboard_id).all()

    return [access.as_dict() for access in user_access]


@view_config(route_name='dashboard_views.get_user_access', renderer='json', permission='view')
def get_dashboards_user_access_view(request):
    """
    Get the logged in user access role for this dashboard
    :param request:
    :return:
    """

    dashboard_id = request.matchdict['id']
    user_access = session.query(UserDashboard).filter(UserDashboard.dashboard_id == dashboard_id,
                                                      UserDashboard.user_id == request.authenticated_userid).first()
    return user_access.as_dict()


@view_config(route_name='dashboard_views.edit_user_access', renderer='json', permission='edit')
def edit_dashboard_user_access_view(request):
    """
    Set user role for this dashboard
    :param request:
    :return:
    """

    dashboard_id = request.matchdict['id']
    user_id = request.json_body['user_id']
    role_name = request.json_body['role']
    user_access = session.query(UserDashboard).filter(UserDashboard.dashboard_id == dashboard_id,
                                                      UserDashboard.user_id == user_id).first()
    role = session.query(Role).filter(Role.name == role_name).first()
    user_access.role = role


@view_config(route_name='dashboard_views.add_user_access', renderer='json', permission='edit')
def add_dashboard_user_access_view(request):
    """
    Add user access role for this dashboard
    :param request:
    :return:
    """

    dashboard_id = request.matchdict['id']
    user_id = request.json_body['user_id']
    role_name = request.json_body['role']
    role = session.query(Role).filter(Role.name == role_name).first()
    user_access = create(UserDashboard, user_id=user_id, dashboard_id=dashboard_id, role_id=role.id)

    return user_access.as_dict()


@view_config(route_name='dashboard_views.delete_user_access', renderer='json', permission='edit')
def delete_dashboard_user_access_view(request):
    """
    Delete user role for this dashboard
    :param request:
    :return:
    """

    dashboard_id = request.matchdict['id']
    user_id = request.params['user_id']
    session.query(UserDashboard). \
        filter(UserDashboard.dashboard_id == dashboard_id, UserDashboard.user_id == user_id). \
        delete(synchronize_session='fetch')

    return {}
