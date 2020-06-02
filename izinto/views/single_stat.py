import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, SingleStat
from izinto.services.single_stat import create_single_stat, list_single_stats, build_copied_stat_title, \
    paste_single_stat


@view_config(route_name='single_stat_views.create_single_stat', renderer='json', permission='add')
def create_single_stat_view(request):
    data = request.json_body
    title = data.get('title')
    query = data.get('query')
    decimals = data.get('decimals', 0)
    stat_format = data.get('format', '')
    thresholds = data.get('thresholds')
    colors = data.get('colors')
    dashboard_id = data.get('dashboard_id')
    data_source_id = data.get('data_source_id')

    # check vital data
    if not (title and query):
        raise exc.HTTPBadRequest(json_body={'message': 'Need title and query'})
    # check threshold and colors values
    if not colors:
        raise exc.HTTPBadRequest(json_body={'message': 'Need a color'})
    if not thresholds:
        if len(colors.split(',')) != 1:
            raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})
    elif len(thresholds.split(',')) != len(colors.split(',')) - 1:
        raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})

    single_stat = create_single_stat(title,
                                     query,
                                     decimals,
                                     stat_format,
                                     thresholds,
                                     colors,
                                     dashboard_id,
                                     data_source_id)
    return single_stat.as_dict()


@view_config(route_name='single_stat_views.get_single_stat', renderer='json', permission='view')
def get_single_stat_view(request):
    """
    Get a single_stat
    :param request:
    :return:
    """
    single_stat_id = request.matchdict.get('id')
    if not single_stat_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need single_stat id'})
    single_stat = session.query(SingleStat).filter(SingleStat.id == single_stat_id).first()
    if not single_stat:
        raise exc.HTTPNotFound(json_body={'message': 'Single Stat not found'})
    single_stat_data = single_stat.as_dict()
    return single_stat_data


@view_config(route_name='single_stat_views.edit_single_stat', renderer='json', permission='edit')
def edit_single_stat_view(request):
    """
    Edit single_stat
    :param request:
    :return:
    """
    data = request.json_body
    single_stat_id = request.matchdict.get('id')
    title = data.get('title')
    query = data.get('query')
    decimals = data.get('decimals', 0)
    frmat = data.get('format', '')
    thresholds = data.get('thresholds', '')
    colors = data.get('colors', '')
    data_source_id = data.get('data_source_id')

    # check vital data
    if not single_stat_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need single stat id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})
    if not query:
        raise exc.HTTPBadRequest(json_body={'message': 'Need query'})
    # check threshold and colors values
    if len(thresholds.split(',')) != len(colors.split(',')) - 1:
        raise exc.HTTPBadRequest(json_body={'message': 'Need one more color than thresholds'})

    single_stat = session.query(SingleStat).filter(SingleStat.id == single_stat_id).first()
    if not single_stat:
        raise exc.HTTPNotFound(json_body={'message': 'Single Stat not found'})

    single_stat.title = title
    single_stat.query = query
    single_stat.decimals = decimals
    single_stat.format = frmat
    single_stat.thresholds = thresholds
    single_stat.colors = colors
    single_stat.data_source_id = data_source_id

    return single_stat.as_dict()


@view_config(route_name='single_stat_views.list_single_stats', renderer='json', permission='view')
def list_single_stats_view(request):
    """
    List single_stats by filters
    :param request:
    :return:
    """
    filters = request.params
    stats = list_single_stats(**filters)

    return [single_stat.as_dict() for single_stat in stats]


@view_config(route_name='single_stat_views.delete_single_stat', renderer='json', permission='delete')
def delete_single_stat_view(request):
    """
    Delete a single_stat view
    :param request:
    :return:
    """
    single_stat_id = request.matchdict.get('id')
    single_stat = session.query(SingleStat).filter(SingleStat.id == single_stat_id).first()
    if not single_stat:
        raise exc.HTTPNotFound(json_body={'message': 'No single stat found.'})

    return session.query(SingleStat). \
        filter(SingleStat.id == single_stat_id). \
        delete(synchronize_session='fetch')


@view_config(route_name='single_stat_views.paste_single_stat', renderer='json', permission='add')
def paste_single_stat_view(request):
    data = request.json_body
    single_stat_id = data.get('id')
    dashboard_id = data.get('dashboard_id')

    # check vital data
    if not single_stat_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need copied single stat'})
    if not dashboard_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need destination dashboard'})

    single_stat = session.query(SingleStat).filter(SingleStat.id == single_stat_id).first()
    title = single_stat.title
    # make "Copy of" title
    if dashboard_id == single_stat.dashboard_id:
        title = build_copied_stat_title(title, dashboard_id)
        
    single_stat = paste_single_stat(single_stat_id, dashboard_id, title)
    return single_stat.as_dict()
