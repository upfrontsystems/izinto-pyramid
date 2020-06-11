from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc

from izinto.models import Collection, Variable, Chart, DataSource, SingleStat, DashboardView
from izinto.tests import BaseTest, dummy_request, add_dashboard, add_user
from izinto.views.dashboard import (create_dashboard_view, get_dashboard_view, edit_dashboard_view,
                                    list_dashboards_view, delete_dashboard_view, paste_dashboard_view,
                                    reorder_dashboard_view, list_dashboard_view_items)


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

        req.json_body = {'title': 'Title', 'description': 'Description'}
        resp = create_dashboard_view(req)
        self.assertEqual(resp['title'], 'Title')

    def test_get_dashboard_view(self):
        dashboard = add_dashboard(self.session, title='Test title')
        req = dummy_request(self.session)

        with self.assertRaises(exc.HTTPBadRequest):
            get_dashboard_view(req)

        req.matchdict = {'id': dashboard.id}
        dashboard = get_dashboard_view(req)
        self.assertEqual(dashboard['title'], 'Test title')

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
