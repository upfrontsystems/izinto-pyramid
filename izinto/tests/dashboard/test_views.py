from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc

from izinto.models import Collection, Variable, Chart, DataSource, SingleStat, DashboardView, Dashboard
from izinto.tests import BaseTest, dummy_request, add_dashboard, add_user
from izinto.views.dashboard import (create_dashboard_view, get_dashboard_view, edit_dashboard_view,
                                    list_dashboards_view, delete_dashboard_view, paste_dashboard_view,
                                    reorder_dashboard_view, list_dashboard_view_items, edit_content_view,
                                    get_content_view)


class TestDashboardViews(BaseTest):
    """ Class for testing dashboard views """

    def setUp(self):
        super(TestDashboardViews, self).setUp()
        self.config = pyramid_testing.setUp()
        self.config.testing_securitypolicy(userid=u'admin', permissive=True)

    def test_create_dashboard(self):
        req = dummy_request(self.session)
        req.json_body = {'description': 'Description'}

        with self.assertRaises(exc.HTTPBadRequest):
            create_dashboard_view(req)

        req.json_body = {'title': 'Title', 'description': 'Description', 'type': 'new',
                         'content': '<h1>Hello world!</h1>'}
        resp = create_dashboard_view(req)
        self.assertEqual(resp['title'], 'Title')
        self.assertEqual(resp['description'], 'Description')
        self.assertEqual(resp['type'], 'new')
        self.assertEqual(resp['content'], '<h1>Hello world!</h1>')

    def test_create_dashboard_in_collection(self):
        collection = Collection(title='Title')
        self.session.add(collection)
        self.session.flush()
        user = add_user(self.session)
        req = dummy_request(self.session)
        req.json_body = {'title': 'Title', 'description': 'Description', 'collection_id': collection.id,
                         'users': [user.as_dict()]}
        resp = create_dashboard_view(req)
        self.assertEqual(resp['title'], 'Title')
        self.assertEqual(resp['collection_id'], collection.id)
        self.assertEqual(resp['index'], 0)
        self.assertEqual(resp['users'][0], user.as_dict())

        req.json_body = {'title': 'Title', 'description': 'Description', 'collection_id': collection.id}
        resp = create_dashboard_view(req)
        self.assertEqual(resp['index'], 1)

    def test_get_dashboard_view(self):
        dashboard = add_dashboard(self.session, title='Test title')
        req = dummy_request(self.session)

        with self.assertRaises(exc.HTTPBadRequest):
            get_dashboard_view(req)

        req.matchdict = {'id': dashboard.id}
        dashboard = get_dashboard_view(req)
        self.assertEqual(dashboard['title'], 'Test title')

    def test_edit_dashboard_view(self):
        collection = Collection(title='Title')
        self.session.add(collection)
        self.session.flush()
        user = add_user(self.session)
        dashboard = add_dashboard(self.session, title='Test title')
        req = dummy_request(self.session)

        with self.assertRaises(exc.HTTPBadRequest):
            edit_dashboard_view(req)

        req.matchdict = {'id': dashboard.id}
        req.json_body = {'title': 'Edit title', 'description': 'Description', 'collection_id': collection.id,
                         'type': 'new', 'content': '<h1>Hello world!</h1>', 'users': [user.as_dict()]}
        dashboard = edit_dashboard_view(req)
        self.assertEqual(dashboard['title'], 'Edit title')
        self.assertEqual(dashboard['description'], 'Description')
        self.assertEqual(dashboard['type'], 'new')
        self.assertEqual(dashboard['content'], '<h1>Hello world!</h1>')
        self.assertEqual(dashboard['users'][0], user.as_dict())

    def test_list_dashboards_view(self):
        user = add_user(self.session)
        self.config.testing_securitypolicy(userid=user.id, permissive=True)
        add_dashboard(self.session, title='Dashboard 1')
        add_dashboard(self.session, title='Dashboard 2')
        add_dashboard(self.session, title='Dashboard 3', users=[user])

        collection = Collection(title='Title')
        self.session.add(collection)
        self.session.flush()
        add_dashboard(self.session, title='Dashboard 4', collection_id=collection.id)
        add_dashboard(self.session, title='Dashboard 5', collection_id=collection.id, users=[user])
        req = dummy_request(self.session)
        req.params = {}
        dashboards = list_dashboards_view(req)
        self.assertEqual(len(dashboards), 5)

        req.params = {'collection_id': None}
        dashboards = list_dashboards_view(req)
        self.assertEqual(len(dashboards), 3)

        req.params = {'collection_id': collection.id}
        dashboards = list_dashboards_view(req)
        self.assertEqual(len(dashboards), 2)

        req.params = {'user_id': True}
        dashboards = list_dashboards_view(req)
        self.assertEqual(len(dashboards), 2)

    def test_delete_dashboard_view(self):
        dashboard = add_dashboard(self.session, title='Dashboard')
        req = dummy_request(self.session)
        req.matchdict = {'id': dashboard.id}

        delete_dashboard_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            get_dashboard_view(req)

    def test_paste_dashboard_view(self):
        collection = Collection(title='Collection 1')
        self.session.add(collection)
        self.session.flush()
        collection_id = collection.id
        collection2 = Collection(title='Collection 2')
        self.session.add(collection2)
        self.session.flush()
        collection2_id = collection2.id
        data_source = DataSource(name='Data source')
        self.session.add(data_source)
        self.session.flush()

        user = add_user(self.session)
        dashboard = add_dashboard(self.session, title='Test title', collection_id=collection.id, users=[user])
        dashboard_id = dashboard.id
        self.session.add(Variable(name='Variable', value='V', dashboard_id=dashboard.id))
        self.session.add(Chart(title='Chart', data_source_id=data_source.id, dashboard_id=dashboard.id))
        self.session.add(Chart(title='Chart', data_source_id=data_source.id, dashboard_id=dashboard.id))
        self.session.add(SingleStat(title='Single stat', data_source_id=data_source.id, dashboard_id=dashboard_id))
        self.session.flush()

        req = dummy_request(self.session)
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            paste_dashboard_view(req)

        req.matchdict = {'id': dashboard_id}
        req.json_body = {'collection_id': collection_id}
        dashboard = paste_dashboard_view(req)
        self.assertEqual(dashboard['title'], 'Copy of Test title')
        self.assertEqual(len(dashboard['variables']), 1)

        req.matchdict = {'id': dashboard_id}
        req.json_body = {'collection_id': collection2_id}
        dashboard = paste_dashboard_view(req)
        self.assertEqual(dashboard['title'], 'Test title')

    def test_reorder_dashboards_view(self):
        req = dummy_request(self.session)
        collection = Collection(title='Collection')
        self.session.add(collection)
        self.session.flush()
        collection_id = collection.id

        req.json_body = {'title': 'Dashboard 1', 'collection_id': collection_id}
        dashboard = create_dashboard_view(req)
        req.json_body = {'title': 'Dashboard 2', 'collection_id': collection_id}
        create_dashboard_view(req)
        req.json_body = {'title': 'Dashboard 3', 'collection_id': collection_id}
        create_dashboard_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            req.json_body = {'collection_id': collection_id,
                             'index': 1}
            reorder_dashboard_view(req)

        req = dummy_request(self.session)
        req.params = {'collection_id': collection_id}

        dashboards = list_dashboards_view(req)
        self.assertEqual(dashboards[0]['index'], 0)
        self.assertEqual(dashboards[0]['id'], dashboard['id'])

        req.matchdict = {'id': dashboard['id']}
        req.json_body = {'collection_id': collection_id,
                         'index': 1}
        reorder_dashboard_view(req)
        dashboards = list_dashboards_view(req)
        self.assertEqual(dashboards[1]['index'], 1)
        self.assertEqual(dashboards[1]['id'], dashboard['id'])

    def test_list_dashboard_view_view(self):
        self.session.add(DashboardView(name='Day', icon='day'))
        self.session.add(DashboardView(name='Month', icon='month'))
        self.session.add(DashboardView(name='Year', icon='year'))
        self.session.flush()

        req = dummy_request(self.session)
        req.params = {}
        dashboard_views = list_dashboard_view_items(req)
        self.assertEqual(len(dashboard_views), 3)
        self.assertEqual(dashboard_views[0]['name'], 'Day')

    def test_edit_content_view(self):
        dashboard = Dashboard(title='New Dashboard Content')
        self.session.add(dashboard)
        self.session.flush()
        req = dummy_request(self.session)
        req.matchdict = {'id': dashboard.id}
        content = b'<html>hello content!</html>'
        req.json_body = {'content': content}
        response = edit_content_view(req)
        self.assertEqual(response.body, content)

    def test_get_content_view(self):
        content = b'<html>hello content!</html>'
        dashboard = Dashboard(title='Get Dashboard Content', content=content)
        self.session.add(dashboard)
        self.session.flush()
        req = dummy_request(self.session)
        req.matchdict = {'id': dashboard.id}
        response = get_content_view(req)
        self.assertEqual(response.body, content)
