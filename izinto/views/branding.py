import os
from base64 import b64encode
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from izinto.models import Branding, session
from izinto.views import get_values, get, edit, create

attrs = ['hostname', 'favicon', 'logo', 'banner']
image_attrs = ['favicon', 'logo', 'banner']
required_attrs = ['hostname']


@view_config(route_name='branding_views.create_branding', renderer='json', permission='add')
def create_branding(request):
    """
    Create a Branding
    :param request:
    :return Branding:
    """

    data = {'hostname': request.POST.get('hostname')}
    # check hostname is unique
    if not data.get('hostname'):
        raise exc.HTTPBadRequest(json_body={'message': 'Hostname required'})
    if session.query(Branding).filter(Branding.hostname == data['hostname']).first():
        raise exc.HTTPBadRequest(json_body={'message': 'Hostname %s already exists' % data['hostname']})

    data['user_id'] = request.authenticated_userid

    # store branding images
    folder_path = ['domains', data['hostname']]
    for fieldname in image_attrs:
        folder_name = os.path.join(*folder_path)
        store_filename = os.path.basename(request.storage.save(request.POST[fieldname], folder=folder_name))
        data[fieldname] = os.path.join(*folder_path, store_filename)

    branding = create(Branding, **data)
    return branding.as_dict()


@view_config(route_name='branding_views.get_branding', renderer='json', permission='view')
def get_branding_view(request):
    """
    Get a branding
    :param request:
    :return:
    """

    branding = get(request, Branding)
    # set image data in response
    for fieldname in image_attrs:
        image_data = b64encode(open(request.storage.path(branding[fieldname]), 'rb').read()).decode('utf-8')
        branding[fieldname] = image_data
    return branding


@view_config(route_name='branding_views.search_branding', renderer='json', permission='view')
def search_branding_view(request):
    """
    Find branding by hostname or user id
    :param request:
    :return:
    """

    branding = None
    if 'hostname' in request.params:
        branding = session.query(Branding).filter(
            Branding.hostname == request.params['hostname']).first()
    if 'user_id' in request.params:
        branding = session.query(Branding).filter(
            Branding.user_id == request.authenticated_userid).first()

    if not branding:
        return {}

    # set image data in response
    data = branding.as_dict()
    for fieldname in image_attrs:
        image_data = b64encode(open(request.storage.path(getattr(branding, fieldname)), 'rb').read()).decode('utf-8')
        data[fieldname] = image_data
    return data



@view_config(route_name='branding_views.edit_branding', renderer='json', permission='edit')
def edit_branding_view(request):
    """
    Edit branding
    :param request:
    :return:
    """

    branding = get(request, Branding, as_dict=False)
    data = {'hostname': request.POST.get('hostname')}
    # check hostname is unique
    if not data.get('hostname'):
        raise exc.HTTPBadRequest(json_body={'message': 'Hostname required'})
    if session.query(Branding).filter(Branding.hostname == data['hostname'], Branding.id != branding.id).first():
        raise exc.HTTPBadRequest(json_body={'message': 'Hostname %s already exists' % data['hostname']})

    # store branding images
    folder_path = ['domains', data['hostname']]
    for fieldname in image_attrs:
        if fieldname in request.POST:
            # delete existing file
            if getattr(branding, fieldname):
                request.storage.delete(getattr(branding, fieldname))

            folder_name = os.path.join(*folder_path)
            store_filename = os.path.basename(request.storage.save(request.POST[fieldname], folder=folder_name))

            data[fieldname] = os.path.join(*folder_path, store_filename)

    edit(branding, **data)
    return branding.as_dict()
