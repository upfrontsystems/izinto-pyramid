from izinto.models import session, Collection, Dashboard, User


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
        query = query.filter(Dashboard.collection_id == kwargs['collection_id']).order_by(Dashboard.order)
    # filter by users that can view the dashboards
    # filter by users that have access to the collection of the dashboard
    if 'user_id' in kwargs:
        user_query = query.join(Dashboard.users).filter(User.id == kwargs['user_id'])
        collection_query = query.join(Dashboard.collections). \
            join(Collection.users).filter(User.id == kwargs['user_id'])
        query = user_query.union(collection_query).order_by(Dashboard.title)

    return query.all()
