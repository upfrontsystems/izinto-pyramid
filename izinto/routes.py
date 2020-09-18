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
                     '/users/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.get_user',
                     '/users/{id}', request_method='GET',
                     factory=make_protected_function(Administrator))

    config.add_route('user_views.edit_user',
                     '/users/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    # chart views
    config.add_route('chart_views.list_charts',
                     '/charts', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.create_chart',
                     '/charts', request_method='POST',
                     factory=make_protected_function(Administrator))

    config.add_route('chart_views.delete_chart',
                     '/charts/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('chart_views.get_chart',
                     '/charts/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('chart_views.edit_chart',
                     '/charts/{id}', request_method='PUT',
                     factory=make_protected_function(Administrator))

    config.add_route('chart_views.reorder_chart',
                     '/charts/{id}/reorder', request_method='PUT',
                     factory=make_protected_function(Administrator))

    config.add_route('chart_views.paste_chart',
                     '/charts/{id}/paste', request_method='POST',
                     factory=make_protected_function(*all_roles))

    # dashboard views
    config.add_route('dashboard_views.list_dashboards',
                     '/dashboards', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.paste_dashboard',
                     '/dashboards/{id}/paste', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.create_dashboard',
                     '/dashboards', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.delete_dashboard',
                     '/dashboards/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.get_dashboard',
                     '/dashboards/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.edit_dashboard',
                     '/dashboards/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.reorder_dashboard',
                     '/dashboards/{id}/reorder', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.list_dashboard_view_items',
                     '/dashboard_views', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('dashboard_views.get_content_view',
                     '/dashboards/{id}/content', request_method='GET',
                     factory=make_public)

    config.add_route('dashboard_views.edit_content_view',
                     '/dashboards/{id}/content', request_method='PUT',
                     factory=make_public)

    # collection views
    config.add_route('collection_views.list_collections',
                     '/collections', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('collection_views.paste_collection',
                     '/collections/{id}/paste', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('collection_views.create_collection',
                     '/collections', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('collection_views.delete_collection',
                     '/collections/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('collection_views.get_collection',
                     '/collections/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('collection_views.edit_collection',
                     '/collections/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    # variable views
    config.add_route('variable_views.list_variables',
                     '/dashboards/{dashboard_id}/variables', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.create_variable',
                     '/dashboards/{dashboard_id}/variables', request_method='POST',
                     factory=make_protected_function(Administrator))

    config.add_route('variable_views.delete_variable',
                     '/dashboards/{dashboard_id}/variables/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('variable_views.get_variable',
                     '/dashboards/{dashboard_id}/variables/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('variable_views.edit_variable',
                     '/dashboards/{dashboard_id}/variables/{id}', request_method='PUT',
                     factory=make_protected_function(Administrator))

    # single_stat views
    config.add_route('single_stat_views.list_single_stats',
                     '/single_stats', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('single_stat_views.create_single_stat',
                     '/single_stats', request_method='POST',
                     factory=make_protected_function(Administrator))

    config.add_route('single_stat_views.delete_single_stat',
                     '/single_stats/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('single_stat_views.get_single_stat',
                     '/single_stats/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('single_stat_views.edit_single_stat',
                     '/single_stats/{id}', request_method='PUT',
                     factory=make_protected_function(Administrator))
    
    config.add_route('single_stat_views.paste_single_stat',
                     '/single_stats/{id}/paste', request_method='POST',
                     factory=make_protected_function(Administrator))

    # data_source views
    config.add_route('data_source_views.list_data_sources',
                     '/data_sources', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('data_source_views.create_data_source',
                     '/data_sources', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('data_source_views.delete_data_source',
                     '/data_sources/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('data_source_views.get_data_source',
                     '/data_sources/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('data_source_views.edit_data_source',
                     '/data_sources/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    config.add_route('data_source_views.query',
                     '/data_sources/{id}/query', request_method='POST',
                     factory=make_protected_function(*all_roles))

    # single_stat views
    config.add_route('script_views.list_scripts',
                     '/scripts', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('script_views.create_script',
                     '/scripts', request_method='POST',
                     factory=make_protected_function(Administrator))

    config.add_route('script_views.delete_script',
                     '/scripts/{id}', request_method='DELETE',
                     factory=make_protected_function(Administrator))

    config.add_route('script_views.get_script',
                     '/scripts/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('script_views.edit_script',
                     '/scripts/{id}', request_method='PUT',
                     factory=make_protected_function(Administrator))

    config.add_route('script_views.reorder_script',
                     '/scripts/{id}/reorder', request_method='PUT',
                     factory=make_protected_function(Administrator))
    # query views
    config.add_route('query_views.list_queries',
                     '/dashboards/{dashboard_id}/queries', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.create_query',
                     '/dashboards/{dashboard_id}/queries', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.delete_query',
                     '/dashboards/{dashboard_id}/queries/{id}', request_method='DELETE',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.get_query',
                     '/dashboards/{dashboard_id}/queries/{id}', request_method='GET',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.edit_query',
                     '/dashboards/{dashboard_id}/queries/{id}', request_method='PUT',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.run_query',
                     '/dashboards/{dashboard_id}/queries/{name}/run', request_method='POST',
                     factory=make_protected_function(*all_roles))

    config.add_route('query_views.test_query',
                     '/dashboards/{dashboard_id}/queries/test', request_method='POST',
                     factory=make_protected_function(*all_roles))
