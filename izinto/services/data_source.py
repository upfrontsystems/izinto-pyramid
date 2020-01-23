from izinto.models import session, DataSource


def get_data_source(data_source_id):
    """
    Get a data source from id
    :param data_source_id:
    :return:
    """

    query = session.query(DataSource).filter(DataSource.id == data_source_id)

    return query.first()
