import re
from izinto.models import session, SingleStat


def create_single_stat(title, query, decimals, stat_format, thresholds, colors, dashboard_id, data_source_id):
    """
    Create single stat
    :param title:
    :param query:
    :param decimals:
    :param stat_format:
    :param thresholds:
    :param colors:
    :param dashboard_id:
    :param data_source_id:
    :return SingleStat:
    """

    stat = SingleStat(title=title,
                      query=query,
                      decimals=decimals,
                      format=stat_format,
                      thresholds=thresholds,
                      colors=colors,
                      dashboard_id=dashboard_id,
                      data_source_id=data_source_id)
    session.add(stat)
    session.flush()

    return stat


def list_single_stats(**kwargs):
    """
    List single stats by filters
    :param kwargs:
    :return:
    """

    query = session.query(SingleStat)
    for column, value in kwargs.items():
        query = query.filter(getattr(SingleStat, column) == value)

    return query.order_by(SingleStat.title).all()


def paste_single_stat(single_stat_id, dashboard_id, title):
    """
    Paste single_stat
    :param single_stat_id:
    :param dashboard_id:
    :param title:
    :return:
    """

    single_stat = session.query(SingleStat).filter(SingleStat.id == single_stat_id).first()
    pasted_single_stat = SingleStat(title=title,
                                    query=single_stat.query,
                                    decimals=single_stat.decimals,
                                    format=single_stat.format,
                                    thresholds=single_stat.thresholds,
                                    colors=single_stat.colors,
                                    dashboard_id=dashboard_id,
                                    data_source_id=single_stat.data_source_id)
    session.add(pasted_single_stat)
    session.flush()

    return pasted_single_stat


def build_copied_stat_title(title, dashboard_id):
    """ Set name and number of copy of title """

    title = 'Copy of %s' % title

    search_str = '%s%s' % (title, '%')
    query = session.query(SingleStat) \
        .filter(SingleStat.dashboard_id == dashboard_id,
                SingleStat.title.ilike(search_str)) \
        .order_by(SingleStat.title.desc()).all()

    if query:
        number = re.search(r'\((\d+)\)', query[0].title)
        if number:
            number = number.group(1)
        if number:
            title = '%s (%s)' % (title, (int(number) + 1))
        else:
            title = '%s (2)' % title
    return title
