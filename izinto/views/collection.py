from pyramid.view import view_config
from izinto.models import session, Collection, User, UserCollection, Dashboard, UserDashboard, Variable, Chart, \
    ChartGroupBy, SingleStat
from izinto.security import Administrator
from izinto.views import paste, create, get_user, get_values, get, edit, delete
from izinto.views.dashboard import attrs as dashboard_attrs
from izinto.views.chart import attrs as chart_attrs

attrs = ['title', 'description']
required_attrs = ['title']


@view_config(route_name='collection_views.create_collection', renderer='json', permission='add')
def create_collection(request):
    """
    Create a Collection
    :param request:
    :return Collection:
    """
    data = get_values(request, attrs, required_attrs)
    users = request.json_body.get('users', [])

    collection = create(Collection, **data)

    # add logged in user to collection
    if not [user for user in users if user['id'] == request.authenticated_userid]:
        create(UserCollection, user_id=request.authenticated_userid, collection_id=collection.id)
    for user in users:
        create(UserCollection, user_id=user['id'], collection_id=collection.id)

    return collection.as_dict()


@view_config(route_name='collection_views.get_collection', renderer='json', permission='view')
def get_collection_view(request):
    """
   Get a collection
   :param request:
   :return:
   """
    collection = get(request, Collection, as_dict=False)

    collection_data = collection.as_dict()
    dashboards = session.query(Dashboard).filter(Dashboard.collection_id == collection.id).all()
    collection_data['dashboards'] = [dash.as_dict() for dash in dashboards]
    return collection_data


@view_config(route_name='collection_views.edit_collection', renderer='json', permission='edit')
def edit_collection(request):
    """
    Edit collection
    :param request:
    :return:
    """
    collection = get(request, Collection, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(collection, **data)

    users = request.json_body.get('users', [])
    collection.users[:] = []
    for user in users:
        collection.users.append(get_user(user['id']))

    return collection.as_dict()


@view_config(route_name='collection_views.list_collections', renderer='json', permission='view')
def list_collections(request):
    """
    List collections
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(Collection)

    user = get_user(request.authenticated_userid)
    if not user.has_role(Administrator):
        query = query.join(Collection.users).filter(User.id == request.authenticated_userid)

    collections = []
    for collection in query.order_by(Collection.title).all():
        cdata = collection.as_dict()
        if 'list_dashboards' in filters:
            dashboards = session.query(Dashboard).filter(Dashboard.collection_id == collection.id).all()
            cdata['dashboards'] = [dash.as_dict() for dash in dashboards]
        collections.append(cdata)

    return collections


@view_config(route_name='collection_views.delete_collection', renderer='json', permission='delete')
def delete_collection(request):
    """
    Delete a collection
    :param request:
    :return:
    """
    return delete(request, Collection)


@view_config(route_name='collection_views.paste_collection', renderer='json', permission='add')
def paste_collection_view(request):
    """
    Paste a Collection view
    :param request:
    :return Collection:
    """
    collection = get(request, Collection, as_dict=False)
    data = {attr: getattr(collection, attr) for attr in attrs}

    pasted_collection = paste(request, Collection, data, None, 'title')

    # copy list of users
    for user in collection.users:
        session.add(UserCollection(user_id=user.id, collection_id=pasted_collection.id))

    # copy dashboards in collection
    for dashboard in collection.dashboards:
        data = {attr: getattr(dashboard, attr) for attr in dashboard_attrs}
        pasted_dashboard = paste(request, Dashboard, data, 'collection_id', 'title')

        # copy list of users
        for user in dashboard.users:
            create(UserDashboard, user_id=user['id'], dashboard_id=dashboard.id)

        # copy list of variables
        for variable in dashboard.variables:
            create(Variable, name=variable, value=variable.value, dashboard_id=pasted_dashboard.id)

        # copy charts
        for chart in session.query(Chart).filter(Chart.dashboard_id == dashboard.id).all():
            data = {attr: getattr(dashboard, attr) for attr in chart_attrs}
            pasted_chart = paste(request, Chart, data, 'dashboard_id', 'title')

            for group in chart.group_by:
                create(ChartGroupBy, chart_id=pasted_chart.id, dashboard_view_id=group.dashboard_view_id,
                       value=group.value)

        # copy single stats
        for stat in session.query(SingleStat).filter(SingleStat.dashboard_id == dashboard.id).all():
            create(SingleStat, title=stat.title, query=stat.query, decimals=stat.decimals, format=stat.format,
                   thresholds=stat.thresholds, colors=stat.colors, dashboard_id=pasted_dashboard.id,
                   data_source_id=stat.data_source_id)

    return pasted_collection.as_dict()
