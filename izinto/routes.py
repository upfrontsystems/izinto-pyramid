from izinto.security import (
    make_protected_function,
    make_public,
    all_roles,
    Administrator,
    User
)


def includeme(config):
    # auth views
    config.add_route('auth_views.register_user',
                     '/auth/register', request_method='POST',
                     factory=make_public)

    config.add_route('auth_views.confirm_otp_registration',
                     '/auth/confirm-otp', request_method='POST',
                     factory=make_public)

    config.add_route('auth_views.login',
                     '/auth/login', request_method='POST',
                     factory=make_public)

    config.add_route('auth_views.logout',
                     '/auth/logout', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('auth_views.reset',
                     '/auth/reset', request_method='POST',
                     factory=make_public)

    config.add_route('auth_views.set_password',
                     '/auth/set-password', request_method='POST',
                     factory=make_public)

    config.add_route('auth_views.list_roles', '/auth/roles', request_method='GET',
                     factory=make_protected_function(*all_roles))

    # user Views
    config.add_route('user_views.list_users',
                     '/users', request_method='GET',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.create_user',
                     '/users', request_method='POST',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.delete_user',
                     '/user/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.get_user',
                     '/user/{id}', request_method='GET',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.edit_user',
                     '/user/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    # chart views
    config.add_route('chart_views.list_charts',
                     '/charts', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.create_chart',
                     '/charts', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.delete_chart',
                     '/chart/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.get_chart',
                     '/chart/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.edit_chart',
                     '/chart/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    # dashboard views
    config.add_route('dashboard_views.list_dashboards',
                     '/dashboards', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.create_dashboard',
                     '/dashboards', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.delete_dashboard',
                     '/dashboard/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.get_dashboard',
                     '/dashboard/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.edit_dashboard',
                     '/dashboard/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    # variable views
    config.add_route('variable_views.list_variables',
                     '/variables', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.create_variable',
                     '/variables', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.delete_variable',
                     '/variable/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.get_variable',
                     '/variable/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.edit_variable',
                     '/variable/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))
