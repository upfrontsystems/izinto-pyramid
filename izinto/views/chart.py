import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Chart
from izinto.services.chart import create_chart, list_charts, get_chart


@view_config(route_name='chart_views.create_chart', renderer='json', permission='add')
def create_chart_view(request):
    data = request.json_body
    title = data.get('title')
    unit = data.get('unit')
    color = data.get('color')
    decimals = data.get('decimals', 2)
    typ = data.get('type')
    query = data.get('query')
    dashboard_id = data.get('dashboard_id')
    data_source_id = data.get('data_source_id')

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})
    if not data_source_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need data source'})

    prev = session.query(Chart).filter(Chart.dashboard_id == dashboard_id).order_by(Chart.index.desc()).first()
    index = 0
    if prev:
        index = prev.index + 1

    chart = create_chart(title, unit, color, decimals, typ, query, dashboard_id, data_source_id, index)
    return chart.as_dict()


@view_config(route_name='chart_views.get_chart', renderer='json', permission='view')
def get_chart_view(request):
    """
   Get a chart
   :param request:
   :return:
   """
    chart_id = request.matchdict.get('id')
    if chart_id is None:
        raise exc.HTTPBadRequest(json_body={'message': 'Need chart id'})
    chart = get_chart(chart_id)
    if not chart:
        raise exc.HTTPNotFound(json_body={'message': 'Chart not found'})
    chart_data = chart.as_dict()
    return chart_data


@view_config(route_name='chart_views.edit_chart', renderer='json', permission='edit')
def edit_chart(request):
    """
    Edit chart
    :param request:
    :return:
    """
    data = request.json_body
    chart_id = request.matchdict.get('id')
    index = data.get('index')
    title = data.get('title')
    unit = data.get('unit')
    color = data.get('color')
    decimals = data.get('decimals')
    typ = data.get('type')
    query = data.get('query')
    data_source_id = data.get('data_source_id')

    # check vital data
    if chart_id is None:
        raise exc.HTTPBadRequest(json_body={'message': 'Need chart id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    chart = get_chart(chart_id=chart_id)
    if not chart:
        raise exc.HTTPNotFound(json_body={'message': 'Chart not found'})

    chart.unit = unit
    chart.index = index
    chart.title = title
    chart.color = color
    chart.decimals = decimals
    chart.type = typ
    chart.query = query
    chart.data_source_id = data_source_id

    chart_data = chart.as_dict()
    return chart_data


@view_config(route_name='chart_views.list_charts', renderer='json', permission='view')
def list_charts_view(request):
    """
    List charts by filters
    :param request:
    :return:
    """
    filters = request.params
    charts = list_charts(**filters)

    return [chart.as_dict() for chart in charts]


@view_config(route_name='chart_views.delete_chart', renderer='json', permission='delete')
def delete_chart(request):
    """
    Delete a chart view
    :param request:
    :return:
    """

    chart_id = request.matchdict.get('id')
    chart = get_chart(chart_id)
    if not chart:
        raise exc.HTTPNotFound(json_body={'message': 'No chart found.'})

    session.query(Chart). \
        filter(Chart.id == chart_id). \
        delete(synchronize_session='fetch')


@view_config(route_name='chart_views.reorder_chart', renderer='json', permission='edit')
def reorder_chart_view(request):
    data = request.json_body
    chart_id = request.matchdict.get('id')
    dashboard_id = data.get('dashboard_id')
    index = data['index']

    chart = get_chart(chart_id)
    if not chart:
        raise exc.HTTPNotFound(json_body={'message': 'No chart found.'})

    reorder = session.query(Chart).filter(Chart.dashboard_id == dashboard_id, Chart.id != chart_id)

    if index > chart.index:
        change = -1
        reorder = reorder.filter(Chart.index.between(chart.index, index)).all()
    else:
        change = 1
        reorder = reorder.filter(Chart.index.between(index, chart.index)).all()

    for reorder_chart in reorder:
        reorder_chart.index += change
    chart.index = index

    return {}
