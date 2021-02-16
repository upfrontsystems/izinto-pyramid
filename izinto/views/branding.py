from pyramid.view import view_config
from izinto.models import Branding
from izinto.views import get_values, get, edit

attrs = ['hostname', 'favicon', 'logo', 'banner']
required_attrs = ['hostname']


@view_config(route_name='branding_views.get_branding', renderer='json', permission='view')
def get_branding_view(request):
    """
    Get a branding
    :param request:
    :return:
    """
    return get(request, Branding)


@view_config(route_name='branding_views.edit_branding', renderer='json', permission='edit')
def edit_branding_view(request):
    """
    Edit branding
    :param request:
    :return:
    """

    branding = get(request, Branding, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(branding, **data)

    return branding.as_dict()