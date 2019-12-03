from izinto.models import session, Chart


def create_chart(title, selector, unit, color, typ, group_by, query, dashboard_id, data_source_id, index):
    """
    Create chart
    :param title:
    :param selector:
    :param unit:
    :param color:
    :param typ:
    :param group_by:
    :param query:
    :param dashboard_id:
    :param data_source_id:
    :param index:
    :return:
    """

    chart = Chart(title=title,
                  selector=selector,
                  unit=unit,
                  color=color,
                  type=typ,
                  group_by=group_by,
                  query=query,
                  dashboard_id=dashboard_id,
                  data_source_id=data_source_id,
                  index=index)
    session.add(chart)
    session.flush()

    return chart


def list_charts(**kwargs):
    """
    List charts by filters
    :param filters:
    :return:
    """

    query = session.query(Chart)
    if 'dashboard_id' in kwargs:
        query = query.filter(Chart.dashboard_id == kwargs['dashboard_id'])

    return query.order_by(Chart.index).all()
