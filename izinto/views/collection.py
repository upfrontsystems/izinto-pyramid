import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Collection, User, UserCollection
from izinto.services.user import get_user
from izinto.services.dashboard import list_dashboards


@view_config(route_name='collection_views.create_collection', renderer='json', permission='add')
def create_collection(request):
    data = request.json_body
    title = data.get('title')
    description = data.get('description')
    users = data.get('users', [])

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    collection = Collection(title=title,
                            description=description)
    session.add(collection)
    session.flush()

    for user in users:
        session.add(UserCollection(user_id=user['id'], collection_id=collection.id))

    return collection.as_dict()


@view_config(route_name='collection_views.get_collection', renderer='json', permission='view')
def get_collection_view(request):
    """
   Get a collection
   :param request:
   :return:
   """
    collection_id = request.matchdict.get('id')
    if not collection_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need collection id'})
    collection = get_collection(collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'Collection not found'})

    collection_data = collection.as_dict()
    collection_data['dashboards'] = [dash.as_dict() for dash in list_dashboards(collection_id=collection_id)]
    return collection_data


def get_collection(collection_id):
    """
    Get a collection
    :param collection_id:
    :return:
    """

    query = session.query(Collection).filter(Collection.id == collection_id)
    return query.first()


@view_config(route_name='collection_views.edit_collection', renderer='json', permission='edit')
def edit_collection(request):
    """
    Edit collection
    :param request:
    :return:
    """
    data = request.json_body
    collection_id = request.matchdict.get('id')
    description = data.get('description')
    title = data.get('title')
    users = data.get('users', [])

    # check vital data
    if not collection_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need collection id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    collection = get_collection(collection_id=collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'Collection not found'})

    collection.description = description
    collection.title = title

    collection.users[:] = []
    for user in users:
        collection.users.append(get_user(user['id']))

    return collection.as_dict()


@view_config(route_name='collection_views.list_collections', renderer='json', permission='view')
def list_collections(request):
    """
    List collections
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(Collection)

    if 'user_id' in filters:
        query = query.join(Collection.users).filter(User.id == request.authenticated_userid)

    return [collection.as_dict() for collection in query.order_by(Collection.title).all()]


@view_config(route_name='collection_views.delete_collection', renderer='json', permission='delete')
def delete_collection(request):
    """
    Delete a collection
    :param request:
    :return:
    """
    collection_id = request.matchdict.get('id')
    collection = get_collection(collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'No collection found.'})

    session.query(Collection). \
        filter(Collection.id == collection_id). \
        delete(synchronize_session='fetch')
