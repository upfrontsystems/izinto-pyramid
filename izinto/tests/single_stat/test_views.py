import pyramid.httpexceptions as exc

from izinto.models import Dashboard, DataSource
from izinto.tests import BaseTest, dummy_request
from izinto.views.single_stat import create_single_stat_view, get_single_stat_view, edit_single_stat_view, \
    list_single_stats_view, delete_single_stat_view


class TestSingleStatViews(BaseTest):

    def test_create_single_stat(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        # Test error validation
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title'}
            create_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'query': 'query'}
            create_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title', 'query': 'query'}
            create_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title', 'query': 'query', 'colors': '#eee,#000'}
            create_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title', 'query': 'query', 'colors': '#eee,#000', 'thresholds': '1,2'}
            create_single_stat_view(req)

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }

        single_stat = create_single_stat_view(req)
        self.assertIsNotNone(single_stat.get('id'))
        self.assertEqual(single_stat['title'], 'Title')

    def test_get_single_stat(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Data source')
        self.session.add(data_source)
        self.session.flush()

        with self.assertRaises(exc.HTTPBadRequest):
            get_single_stat_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            get_single_stat_view(req)

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }

        single_stat = create_single_stat_view(req)
        single_stat_id = single_stat['id']
        req.matchdict = {'id': single_stat_id}

        single_stat = get_single_stat_view(req)
        self.assertEqual(single_stat_id, single_stat['id'])

    def test_edit_single_stat(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Data source')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }

        single_stat = create_single_stat_view(req)
        single_stat_id = single_stat['id']

        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict = {'id': single_stat_id}
            edit_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title'}
            create_single_stat_view(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'title': 'Title', 'query': 'query'}
            create_single_stat_view(req)

        req.json_body = {
            'title': 'Edited',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            edit_single_stat_view(req)

        req.matchdict = {'id': single_stat_id}
        edit_single_stat_view(req)

        single_stat = get_single_stat_view(req)
        self.assertEqual(single_stat['title'], 'Edited')

    def test_list_single_stats(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        dashboard2 = Dashboard(title='Dashboard Title 2')
        self.session.add(dashboard2)
        data_source = DataSource(name='Data source')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'Title 1',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }
        single_stat = create_single_stat_view(req)
        req.json_body = {
            'title': 'Title 2',
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }
        create_single_stat_view(req)

        req.json_body = {
            'title': 'Title 3',
            'dashboard_id': dashboard2.id,
            'data_source_id': data_source.id,
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }
        create_single_stat_view(req)

        req = dummy_request(self.session)
        req.params = {}
        single_stats = list_single_stats_view(req)
        self.assertEqual(len(single_stats), 3)

        req.params = {'dashboard_id': dashboard.id}
        single_stats = list_single_stats_view(req)
        self.assertEqual(len(single_stats), 2)
        self.assertEqual(single_stats[0]['id'], single_stat['id'])

    def test_delete_single_stat(self):
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
            'query': 'query',
            'colors': '#eee,#000',
            'thresholds': '1'
        }
        single_stat = create_single_stat_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 0}
            delete_single_stat_view(req)

        req.matchdict = {"id": single_stat['id']}
        delete_single_stat_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            get_single_stat_view(req)
