import re
from izinto.models import session, Chart, ChartGroupBy


def create_chart(title, unit, color, decimals, typ, query, dashboard_id, data_source_id, group_by, index,
                 labels, min_val, max_val, height):
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
    :param group_by:
    :param index:
    :param labels:
    :param min_val:
    :param max_val:
    :param height:
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
                  index=index,
                  labels=labels,
                  min=min_val,
                  max=max_val,
                  height=height)
    session.add(chart)
    session.flush()

    for group in group_by:
        session.add(ChartGroupBy(chart_id=chart.id,
                                 dashboard_view_id=group['dashboard_view_id'],
                                 value=group['value']))

    return chart


def list_charts(**kwargs):
    """
    List charts by filters
    :param kwargs:
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


def paste_chart(chart_id, dashboard_id, title, index):
    """
    Paste chart
    :param chart_id:
    :param dashboard_id:
    :param title:
    :param index:
    :return:
    """

    chart = get_chart(chart_id)
    pasted_chart = Chart(title=title,
                         unit=chart.unit,
                         color=chart.color,
                         decimals=chart.decimals,
                         type=chart.type,
                         query=chart.query,
                         dashboard_id=dashboard_id,
                         data_source_id=chart.data_source_id,
                         labels=chart.labels,
                         min=chart.min,
                         max=chart.max,
                         height=chart.height,
                         index=index)
    session.add(pasted_chart)
    session.flush()

    for group in chart.group_by:
        session.add(ChartGroupBy(chart_id=pasted_chart.id,
                                 dashboard_view_id=group.dashboard_view_id,
                                 value=group.value))

    return pasted_chart


def build_copied_chart_title(title, dashboard_id):
    """ Set name and number of copy of title """

    title = 'Copy of %s' % title

    search_str = '%s%s' % (title, '%')
    query = session.query(Chart) \
        .filter(Chart.dashboard_id == dashboard_id,
                Chart.title.ilike(search_str)) \
        .order_by(Chart.title.desc()).all()

    if query:
        number = re.search(r'\((\d+)\)', query[0].title)
        if number:
            number = number.group(1)
        if number:
            title = '%s (%s)' % (title, (int(number) + 1))
        else:
            title = '%s (2)' % title
    return title
