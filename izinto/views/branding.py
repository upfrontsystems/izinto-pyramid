import os
from base64 import b64encode
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from PIL import Image
from izinto.models import Branding, session
from izinto.views import get, edit, create

attrs = ['hostname', 'favicon', 'logo', 'logo_mobile', 'banner']
image_attrs = ['favicon', 'logo', 'logo_mobile', 'banner']
required_attrs = ['hostname']
sizes = [72, 96, 128, 144, 152, 192, 384, 512]


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
        # create different logo sizes
        if fieldname == 'logo':
            img = Image.open(request.POST[fieldname].file)
            for size in sizes:
                img = img.resize((size, size), Image.LANCZOS)
                resized_name = store_filename.replace('logo', 'logo-%sx%s' % (size, size))
                resized_path = os.path.abspath(request.storage.path(
                    os.path.join(*folder_path, resized_name)))
                img.save(resized_path)

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
                for size in sizes:
                    path = getattr(branding, fieldname)
                    resized_name = ('logo-%sx%s' % (size, size)).join(path.rsplit('logo', 1))
                    request.storage.delete(resized_name)

            folder_name = os.path.join(*folder_path)
            store_filename = os.path.basename(request.storage.save(request.POST[fieldname], folder=folder_name))
            data[fieldname] = os.path.join(*folder_path, store_filename)

            # create different logo sizes
            if fieldname == 'logo':
                img = Image.open(request.POST[fieldname].file)
                for size in sizes:
                    img = img.resize((size, size), Image.LANCZOS)
                    resized_name = store_filename.replace('logo', 'logo-%sx%s' % (size, size))
                    resized_path = os.path.abspath(request.storage.path(
                        os.path.join(*folder_path, resized_name)))
                    img.save(resized_path)

    edit(branding, **data)
    return branding.as_dict()
