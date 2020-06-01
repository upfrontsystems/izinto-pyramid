from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc
from izinto.tests import BaseTest, dummy_request, add_dashboard
from izinto.views.dashboard import (create_dashboard_view, get_dashboard_view, edit_dashboard_view,
                                    list_dashboards_view, delete_dashboard_view, paste_dashboard_view,
                                    reorder_dashboard_view)


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
