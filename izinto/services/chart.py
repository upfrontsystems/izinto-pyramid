from izinto.models import session, Chart


def create_chart(title, unit, color, decimals, typ, query, dashboard_id, data_source_id, index):
    """
    Create chart
    :param title:
    :param unit:
    :param color:
    :param decimals:
    :param typ:
    :param query:
    :param dashboard_id:
    :param data_source_id:
    :param index:
    :return:
    """

    chart = Chart(title=title,
                  unit=unit,
                  color=color,
                  decimals=decimals,
                  type=typ,
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


def get_chart(chart_id=None, dashboard_id=None):
    """
    Get a chart
    :param chart_id:
    :param dashboard_id:
    :return:
    """

    query = session.query(Chart)

    if chart_id is not None:
        query = query.filter(Chart.id == chart_id)
    if dashboard_id:
        query = query.filter(Chart.dashboard_id == dashboard_id)

    return query.first()
