# Views package
import pyramid.httpexceptions as exc
from izinto.models import session


def get_values(request, attrs, required_attrs):
    data = request.json_body
    values = {}
    for attr in attrs:
        value = data.get(attr, None)
        if value is None and attr in required_attrs:
            raise exc.HTTPBadRequest(json_body={'message': '%s required' % attr})
        values[attr] = value
    return values


def create(model, **kwargs):
    obj = model(**kwargs)
    session.add(obj)
    session.flush()
    return obj


def edit(obj, **kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)
    session.flush()


def get(request, model, as_dict=True):
    """
    Get a record
    :param request: HTTP Request
    :param model: SQLAlchemy model instance
    :return:
    """
    record_id = request.matchdict.get('id')
    if not record_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need record id'})
    record = session.query(model).filter(model.id == record_id).first()
    if not record:
        raise exc.HTTPNotFound(json_body={'message': 'record not found'})
    if as_dict:
        return record.as_dict()
    else:
        return record


def filtered_list(request, model, order_by):
    """
    List records and filter if filters specified
    :param request: HTTP Request
    :param model: SQLAlchemy model instance
    :param order_by: SQLAlchemy column
    :return:
    """
    filters = request.params
    query = session.query(model)
    for column, value in filters.items():
        query = query.filter(getattr(model, column) == value)

    return [record.as_dict() for record in query.order_by(order_by).all()]


def delete(request, model):
    """
    Delete a script view
    :param request: HTTP Request
    :param model: SQLAlchemy model instance
    :return:
    """
    record_id = request.matchdict.get('id')
    record = session.query(model).filter(model.id == record_id).first()
    if not record:
        raise exc.HTTPNotFound(json_body={'message': 'Record not found.'})

    return session.query(model). \
        filter(model.id == record_id). \
        delete(synchronize_session='fetch')


def reorder(new_position, record, model, query):
    """ Reorder records by updating `index` column """
    current_position = record.index
    column = getattr(model, 'index')
    if new_position > current_position:
        change = -1
        records = query.filter(column.between(current_position+1, new_position)).all()
    else:
        change = 1
        records = query.filter(column.between(new_position, current_position-1)).all()
    for r in records:
        new_index = getattr(r, column.name) + change
        setattr(r, column.name, new_index)
    setattr(record, column.name, new_position)
    session.flush()

