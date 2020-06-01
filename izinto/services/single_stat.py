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
