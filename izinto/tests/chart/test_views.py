import pyramid.httpexceptions as exc

from izinto.models import Dashboard, DataSource, DashboardView
from izinto.tests import BaseTest, dummy_request
from izinto.views.chart import (create_chart_view, get_chart_view, edit_chart, list_charts_view, delete_chart,
                                reorder_chart_view, paste_chart_view)


class TestChartViews(BaseTest):

    def test_create_chart(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        # Test error validation
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'data_source_id': data_source.id,
                'dashboard_id': dashboard.id
            }
            create_chart_view(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'title': 'Title',
                'dashboard_id':  dashboard.id
            }
            create_chart_view(req)

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }

        chart = create_chart_view(req)
        self.assertIsNotNone(chart.get('id'))
        self.assertEqual(chart['unit'], 'U')

        req.json_body = {
            'title': 'Title 2',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        chart2 = create_chart_view(req)
        self.assertEqual(chart2['index'], 1)

    def test_get_chart(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        with self.assertRaises(exc.HTTPBadRequest):
            get_chart_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            get_chart_view(req)

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }

        chart = create_chart_view(req)
        chart_id = chart['id']
        req.matchdict = {'id': chart_id}

        chart = get_chart_view(req)
        self.assertEqual(chart_id, chart['id'])

    def test_edit_chart(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }

        chart = create_chart_view(req)
        chart_id = chart['id']

        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_chart(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict = {'id': chart_id}
            edit_chart(req)
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            req.json_body = {'title': 'Title'}
            edit_chart(req)

        req.matchdict = {'id': chart_id}
        req.json_body = {
            'title': 'Title Edit',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'R'
        }
        edit_chart(req)

        chart = get_chart_view(req)
        self.assertEqual(chart['title'], 'Title Edit')

    def test_list_charts(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        dashboard2 = Dashboard(title='Dashboard Title 2')
        self.session.add(dashboard2)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        chart = create_chart_view(req)

        req.json_body = {
            'title': 'Title 2',
            'dashboard_id': dashboard2.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        create_chart_view(req)

        req = dummy_request(self.session)
        req.params = {}
        charts = list_charts_view(req)
        self.assertEqual(len(charts), 2)

        req.params = {'dashboard_id': dashboard.id}
        charts = list_charts_view(req)
        self.assertEqual(len(charts), 1)
        self.assertEqual(charts[0]['id'], chart['id'])

    def test_delete_chart(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        chart = create_chart_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 0}
            delete_chart(req)

        req.matchdict = {"id": chart['id']}
        delete_chart(req)

        with self.assertRaises(exc.HTTPNotFound):
            get_chart_view(req)

    def test_reorder_charts(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        chart = create_chart_view(req)
        req.json_body = {
            'title': 'Title 2',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'unit': 'U'
        }
        create_chart_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            req.json_body = {'dashboard_id': dashboard.id,
                             'index': 1}
            reorder_chart_view(req)

        req = dummy_request(self.session)
        req.params = {}

        charts = list_charts_view(req)
        self.assertEqual(charts[0]['id'], chart['id'])

        req.matchdict = {'id': chart['id']}
        req.json_body = {'dashboard_id': dashboard.id,
                         'index': 1}
        reorder_chart_view(req)
        charts = list_charts_view(req)
        self.assertEqual(charts[1]['id'], chart['id'])
        self.assertEqual(charts[1]['index'], 1)
        self.assertEqual(charts[0]['index'], 0)

    def test_copy_chart(self):
        req = dummy_request(self.session)
        dashboard_view = DashboardView(name='Dashboard View', icon='icon')
        self.session.add(dashboard_view)
        dashboard1 = Dashboard(title='Dashboard Title 1')
        self.session.add(dashboard1)
        dashboard2 = Dashboard(title='Dashboard Title 2')
        self.session.add(dashboard2)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard1.id,
            'data_source_id': data_source.id,
            'unit': 'U',
            'group_by': [{'dashboard_view_id': dashboard_view.id, 'value': 1}]
        }

        chart = create_chart_view(req)
        chart_id = chart['id']

        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            paste_chart_view(req)

        req.matchdict = {'id': chart_id}
        req.json_body = {'dashboard_id': dashboard1.id}
        chart = paste_chart_view(req)

        req.matchdict = {'id': chart['id']}
        chart = get_chart_view(req)
        self.assertEqual(chart['title'], 'Copy of Title')

        req.matchdict = {'id': chart_id}
        req.json_body = {'dashboard_id': dashboard2.id}
        chart = paste_chart_view(req)

        req.matchdict = {'id': chart['id']}
        chart = get_chart_view(req)
        self.assertEqual(chart['title'], 'Title')
