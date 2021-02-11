import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import SingleStat
from izinto.views import get_values, create, get, edit, filtered_list, delete, paste

attrs = ['title', 'query', 'decimals', 'format', 'thresholds', 'colors', 'dashboard_id', 'data_source_id']
required_attrs = ['title', 'query', 'colors']


@view_config(route_name='single_stat_views.create_single_stat', renderer='json', permission='add')
def create_single_stat_view(request):
    """
    Create SingleStat
    :param request:
    :return SingleStat:
    """

    data = get_values(request, attrs, required_attrs)

    thresholds = request.json_body.get('thresholds')
    colors = request.json_body.get('colors')
    if not thresholds:
        if len(colors.split(',')) != 1:
            raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})
    elif len(thresholds.split(',')) != len(colors.split(',')) - 1:
        raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})
    if data.get('decimals') is None:
        data['decimals'] = 0
    if data.get('format') is None:
        data['format'] = ''

    stat = create(SingleStat, **data)
    return stat.as_dict()


@view_config(route_name='single_stat_views.get_single_stat', renderer='json', permission='view')
def get_single_stat_view(request):
    """
    Get a single_stat
    :param request:
    :return:
    """
    return get(request, SingleStat)


@view_config(route_name='single_stat_views.edit_single_stat', renderer='json', permission='edit')
def edit_single_stat_view(request):
    """
    Edit single_stat
    :param request:
    :return:
    """

    single_stat = get(request, SingleStat, as_dict=False)
    thresholds = request.json_body.get('thresholds', '')
    colors = request.json_body.get('colors', '')

    # check threshold and colors values
    if len(thresholds.split(',')) != len(colors.split(',')) - 1:
        raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})

    data = get_values(request, attrs, required_attrs)
    edit(single_stat, **data)

    return single_stat.as_dict()


@view_config(route_name='single_stat_views.list_single_stats', renderer='json', permission='view')
def list_single_stats_view(request):
    """
    List single_stats by filters
    :param request:
    :return:
    """
    return filtered_list(request.params, SingleStat, SingleStat.title)


@view_config(route_name='single_stat_views.delete_single_stat', renderer='json', permission='delete')
def delete_single_stat_view(request):
    """
    Delete a single_stat view
    :param request:
    :return:
    """
    return delete(request, SingleStat)


@view_config(route_name='single_stat_views.paste_single_stat', renderer='json', permission='add')
def paste_single_stat_view(request):
    """
    Paste a SingleStat view
    :param request:
    :return SingleStat:
    """
    single_stat = get(request, SingleStat, as_dict=False)
    data = {attr: getattr(single_stat, attr) for attr in attrs}

    pasted_stat = paste(request, SingleStat, data, 'dashboard_id', 'title')
    return pasted_stat.as_dict()
