import re
from izinto.models import session, Collection, Dashboard, User, UserDashboard
from izinto.services.variable import create_variable
from izinto.services.chart import create_chart, list_charts


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


def list_dashboards(**kwargs):
    """
    List dashboards
    :param kwargs:
    :return:
    """
    query = session.query(Dashboard)

    if 'collection_id' in kwargs:
        # filter for dashboards in a collection, and dashboard not in a collection
        if kwargs['collection_id']:
            query = query.filter(Dashboard.collection_id == kwargs['collection_id']).order_by(Dashboard.order)
        else:
            query = query.filter(Dashboard.collection_id == None).order_by(Dashboard.order)
    # filter by users that can view the dashboards
    # filter by users that have access to the collection of the dashboard
    if 'user_id' in kwargs:
        user_query = query.join(Dashboard.users).filter(User.id == kwargs['user_id'])
        collection_query = query.join(Dashboard.collections). \
            join(Collection.users).filter(User.id == kwargs['user_id'])
        query = user_query.union(collection_query).order_by(Dashboard.title)

    return query.all()


def paste_dashboard(dashboard_id, collection_id, title, order):
    """
    Paste dashboard
    :param dashboard_id:
    :param collection_id:
    :param title:
    :param order:
    :return:
    """

    dashboard = get_dashboard(dashboard_id)
    pasted_dashboard = Dashboard(title=title,
                                 description=dashboard.description,
                                 collection_id=collection_id,
                                 order=order)
    session.add(pasted_dashboard)
    session.flush()

    # copy list of users
    for user in dashboard.users:
        session.add(UserDashboard(user_id=user.id, dashboard_id=pasted_dashboard.id))

    # copy list of variables
    for variable in dashboard.variables:
        create_variable(variable.name, variable.value, pasted_dashboard.id)

    # copy charts
    for chart in list_charts(dashboard_id=dashboard_id):
        create_chart(chart.title, chart.selector, chart.unit, chart.color, chart.type, chart.group_by,
                     chart.query, pasted_dashboard.id, chart.data_source_id, chart.index)

    return pasted_dashboard


def build_copied_dashboard_title(title, collection_id):
    """ Set name and number of copy of title """

    title = 'Copy of %s' % title

    search_str = '%s%s' % (title, '%')
    query = session.query(Dashboard) \
        .filter(Dashboard.collection_id == collection_id,
                Dashboard.title.ilike(search_str)) \
        .order_by(Dashboard.title.desc()).all()

    if query:
        number = re.search(r'\((\d+)\)', query[0].title)
        if number:
            number = number.group(1)
        if number:
            title = '%s (%s)' % (title, (int(number) + 1))
        else:
            title = '%s (2)' % title
    return title
