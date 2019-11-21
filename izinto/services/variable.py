from izinto.models import session, Variable


def create_variable(name, value, dashboard_id):
    """ Create a variable
        :param name:
        :param value:
        :param dashboard_id:
    """

    variable = Variable(name=name,
                        value=value,
                        dashboard_id=dashboard_id)
    session.add(variable)
    session.flush()

    return variable.as_dict()


def get_variable(variable_id=None, name=None, dashboard_id=None):
    """
    Get a variable
    :param variable_id:
    :param name:
    :param dashboard_id:
    :return:
    """

    query = session.query(Variable)

    if variable_id:
        query = query.filter(Variable.id == variable_id)
    if name and dashboard_id:
        query = query.filter_by(name=name, dashboard_id=dashboard_id)

    return query.first()


def edit_variable(variable_id, name, value):
    """
    Edit variable
    :param variable_id:
    :param name:
    :param value:
    :return:
    """

    variable = get_variable(variable_id)
    variable.name = name
    variable.value = value
    return variable


def delete_variable(variable_id):
    """
    Delete a variable
    :param variable_id:
    :return:
    """

    return session.query(Variable). \
        filter(Variable.id == variable_id). \
        delete(synchronize_session='fetch')
