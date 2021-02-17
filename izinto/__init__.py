from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from izinto.security import Authenticated, make_protected, OAuthPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings,
                          root_factory=make_protected(Authenticated))
    config.include('pyramid_jinja2')
    config.include('pyramid_mailer')
    config.include('pyramid_storage')
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Authentication and Authorization
    config.set_authentication_policy(OAuthPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_default_permission('view')

    if not global_config.get('testing', None):
        config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
