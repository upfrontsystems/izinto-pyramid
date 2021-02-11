# Views package
import re

import pyramid.httpexceptions as exc
from sqlalchemy import func

from izinto.models import session, User, Role


def get_values(request, attrs, required_attrs):
    data = request.json_body
    values = {}
    for attr in attrs:
        value = data.get(attr, None)
        if value is None and attr in required_attrs:
            raise exc.HTTPBadRequest(json_body={'message': '%s required' % attr})
        # encode image data
        if attr == 'image' and value:
            value = value.encode('utf-8')
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
    :param as_dict:
    :return:
    """
    record_id = request.matchdict.get('id')
    if not record_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need record id'})
    record = session.query(model).filter(model.id == record_id).first()
    if not record:
        raise exc.HTTPNotFound(json_body={'message': 'Record not found'})
    if as_dict:
        return record.as_dict()
    else:
        return record


def filtered_list(filters, model, order_by):
    """
    List records and filter if filters specified
    :param filters: Dictionary
    :param model: SQLAlchemy model instance
    :param order_by: SQLAlchemy column
    :return:
    """
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
        records = query.filter(column.between(current_position + 1, new_position)).all()
    else:
        change = 1
        records = query.filter(column.between(new_position, current_position - 1)).all()
    for r in records:
        new_index = getattr(r, column.name) + change
        setattr(r, column.name, new_index)
    setattr(record, column.name, new_position)
    session.flush()


def paste(request, model, copied_data, parent_id_attribute, name_attribute):
    """ Create a copy of the record """

    data = request.json_body
    parent_id = data.get(parent_id_attribute)
    record = get(request, model, as_dict=False)
    name = getattr(record, name_attribute)

    # make "Copy of" name when pasting in same parent
    if not parent_id or (parent_id == getattr(record, parent_id_attribute)):
        name = 'Copy of %s' % name
        search_str = '%s%s' % (name, '%')
        query = session.query(model).filter(getattr(model, name_attribute).ilike(search_str)) \
            .order_by(getattr(model, name_attribute).desc())
        if parent_id:
            query = query.filter(getattr(model, parent_id_attribute) == parent_id)
        query = query.all()
        if query:
            number = re.search(r'\((\d+)\)', getattr(query[0], name_attribute))
            if number and number.group(1):
                name = '%s (%s)' % (name, (int(number.group(1)) + 1))
            else:
                name = '%s (2)' % name

    # set new record index value if it has one
    if hasattr(model, 'index'):
        result = session.query(func.count(getattr(model, 'id')))
        if parent_id:
            result = result.filter(getattr(model, parent_id_attribute) == parent_id)
        copied_data['index'] = result.first()[0]

    copied_data[name_attribute] = name
    if parent_id_attribute:
        copied_data[parent_id_attribute] = parent_id

    return create(model, **copied_data)


def get_user(user_id=None, telephone=None, email=None, role=None, inactive=None):
    """
    Get a user
    :param user_id:
    :param telephone:
    :param email:
    :param role:
    :param inactive:
    :return:
    """

    query = session.query(User)

    if inactive is not None:
        query = query.filter(User.inactive == inactive)

    if user_id:
        query = query.filter(User.id == user_id)

    if telephone:
        query = query.filter(User.telephone == telephone)

    # case insensitive match by email
    if email:
        query = query.filter(User.email.ilike(email))

    if role:
        query = query.join(User.roles).filter(Role.name == role)

    return query.first()
