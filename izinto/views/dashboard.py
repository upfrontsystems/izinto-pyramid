from pyramid.view import view_config
from sqlalchemy import func
from izinto.models import session, Dashboard, UserDashboard, Variable, Chart, ChartGroupBy, SingleStat, User, \
    DashboardView
from izinto.views import get_values, create, get, edit, filtered_list, delete, paste, reorder, get_user
from izinto.views.chart import attrs as chart_attrs

attrs = ['title', 'description', 'collection_id']
required_attrs = ['title']


@view_config(route_name='dashboard_views.create_dashboard', renderer='json', permission='add')
def create_dashboard_view(request):
    """
    Create Dashboard
    :param request:
    :return Dashboard:
    """

    data = get_values(request, attrs, required_attrs)
    users = request.json_body.get('users', [])
    collection_id = request.json_body.get('collection_id')

    if data.get('index') is None and collection_id:
        result = session.query(func.count(Dashboard.id)).filter(Dashboard.collection_id == collection_id).first()
        data['index'] = result[0]

    dashboard = create(Dashboard, **data)
    # add logged in user to dashboard
    if not [user for user in users if user['id'] == request.authenticated_userid]:
        create(UserDashboard, user_id=request.authenticated_userid, dashboard_id=dashboard.id)

    for user in users:
        create(UserDashboard, user_id=user['id'], dashboard_id=dashboard.id)

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

    users = request.json_body.get('users', [])
    dashboard.users[:] = []
    for user in users:
        dashboard.users.append(get_user(user['id']))

    return dashboard.as_dict()


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

    query = session.query(Dashboard)

    # filter dashboards either by collection or users
    if 'collection_id' in filters:
        # filter for dashboards in a collection, and dashboard not in a collection
        if filters['collection_id']:
            query = query.filter(Dashboard.collection_id == filters['collection_id']).order_by(Dashboard.index)
        else:
            query = query.filter(Dashboard.collection_id == None).order_by(Dashboard.index)
    elif 'user_id' in filters:
        # filter by users that can view the dashboards
        query = query.join(Dashboard.users).filter(User.id == filters['user_id'])

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

    # copy list of users
    for user in dashboard.users:
        create(UserDashboard, user_id=user.id, dashboard_id=pasted_dashboard.id)

    # copy list of variables
    for variable in dashboard.variables:
        create(Variable, name=variable.name, value=variable.value, dashboard_id=pasted_dashboard.id)

    # copy charts
    for chart in session.query(Chart).filter(Chart.dashboard_id == dashboard.id).all():
        data = {attr: getattr(chart, attr) for attr in chart_attrs}
        data['dashboard_id'] = pasted_dashboard.id
        pasted_chart = create(Chart, **data)

        for group in chart.group_by:
            create(ChartGroupBy, chart_id=pasted_chart.id, dashboard_view_id=group.dashboard_view_id, value=group.value)

    # copy single stats
    for stat in session.query(SingleStat).filter(SingleStat.dashboard_id == dashboard.id).all():
        create(SingleStat, title=stat.title, query=stat.query, decimals=stat.decimals, format=stat.format,
               thresholds=stat.thresholds, colors=stat.colors, dashboard_id=pasted_dashboard.id,
               data_source_id=stat.data_source_id)

    return pasted_dashboard.as_dict()


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
