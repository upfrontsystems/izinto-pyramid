from pyramid.view import view_config
from izinto.models import session, Chart, ChartGroupBy
from izinto.views import get_values, create, get, edit, filtered_list, delete, reorder, paste

attrs = ['title', 'unit', 'color', 'decimals', 'type', 'query', 'dashboard_id', 'data_source_id', 'labels', 'min',
         'max', 'height']
required_attrs = ['title', 'data_source_id']


@view_config(route_name='chart_views.create_chart', renderer='json', permission='add')
def create_chart_view(request):
    """
    Create Chart
    :param request:
    :return Chart:
    """

    data = get_values(request, attrs, required_attrs)
    group_by = request.json_body.get('group_by', [])

    if data.get('decimals') is None:
        data['decimals'] = 2
    if data.get('index') is None:
        prev = session.query(Chart).filter_by(dashboard_id=data['dashboard_id']).order_by(Chart.index.desc()).first()
        index = 0
        if prev:
            index = prev.index + 1
        data['index'] = index

    chart = create(Chart, **data)
    for group in group_by:
        group['chart_id'] = chart.id
        create(ChartGroupBy, **group)

    return chart.as_dict()


@view_config(route_name='chart_views.get_chart', renderer='json', permission='view')
def get_chart_view(request):
    """
    Get a chart
    :param request:
    :return:
    """
    return get(request, Chart)


@view_config(route_name='chart_views.edit_chart', renderer='json', permission='edit')
def edit_chart(request):
    """
    Edit chart
    :param request:
    :return:
    """
    chart = get(request, Chart, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(chart, **data)

    group_by = request.json_body.get('group_by', [])
    for group in chart.group_by:
        for data in group_by:
            if data['dashboard_view_id'] == group.dashboard_view_id:
                group.value = data['value']
                break

    return chart.as_dict()


@view_config(route_name='chart_views.list_charts', renderer='json', permission='view')
def list_charts_view(request):
    """
    List charts by filters
    :param request:
    :return:
    """
    return filtered_list(request, Chart, Chart.index)


@view_config(route_name='chart_views.delete_chart', renderer='json', permission='delete')
def delete_chart(request):
    """
    Delete a chart view
    :param request:
    :return:
    """
    return delete(request, Chart)


@view_config(route_name='chart_views.reorder_chart', renderer='json', permission='edit')
def reorder_chart_view(request):
    """
    Delete a chart view
    :param request:
    :return:
    """
    chart = get(request, Chart, as_dict=False)
    data = get_values(request, ['index'], ['index'])
    dashboard_scripts = session.query(Chart).filter(chart.dashboard_id == chart.dashboard_id)
    reorder(data.get('index'), chart, Chart, dashboard_scripts)
    return {}


@view_config(route_name='chart_views.paste_chart', renderer='json', permission='add')
def paste_chart_view(request):
    """
    Paste a chart view
    :param request:
    :return Chart:
    """

    chart = get(request, Chart, as_dict=False)
    data = {attr: getattr(chart, attr) for attr in attrs}

    pasted_chart = paste(request, Chart, data, 'dashboard_id', 'title')

    for group in chart.group_by:
        create(ChartGroupBy, chart_id=pasted_chart.id, dashboard_view_id=group.dashboard_view_id, value=group.value)

    return pasted_chart.as_dict()
