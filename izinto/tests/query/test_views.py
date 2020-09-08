import pyramid.httpexceptions as exc

from izinto.models import Query, DataSource
from izinto.tests import BaseTest, dummy_request, add_dashboard
from izinto.views.query import (create_query_view, get_query_view, list_queries_view, delete_query_view,
                                edit_query_view)


class TestQueryViews(BaseTest):

    def test_create_query(self):
        datasource = DataSource(name='datasource')
        self.session.add(datasource)
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        req = dummy_request(self.session)
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            create_query_view(req)

        req.json_body = {'name': 'Query',
                         'query': 'query string',
                         'data_source_id': datasource.id,
                         'dashboard_id': dash.id}
        query = create_query_view(req)

        self.assertIsNotNone(query['id'])
        self.assertEqual(query['name'], 'Query')
        self.assertEqual(query['dashboard_id'], dash.id)

    def test_get_query(self):
        datasource = DataSource(name='datasource')
        self.session.add(datasource)
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        query = Query(name='Query', query='query string', dashboard_id=dash.id, data_source_id=datasource.id)
        self.session.add(query)
        self.session.flush()
        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            get_query_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict['id'] = 100
            get_query_view(req)

        req.matchdict['id'] = query.id
        resp = get_query_view(req)

        self.assertEqual(resp['id'], query.id)
        self.assertEqual(resp['name'], 'Query')

    def test_edit_query(self):
        datasource = DataSource(name='datasource')
        self.session.add(datasource)
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        query = Query(name='Query', query='query string', dashboard_id=dash.id, data_source_id=datasource.id)
        self.session.add(Query(name='Query2', query='query string 2', dashboard_id=dash.id, data_source_id=datasource.id))
        self.session.add(query)
        self.session.flush()

        req = dummy_request(self.session)
        req.matchdict = {}
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_query_view(req)
        req.matchdict['id'] = 100
        req.json_body = {'name': 'Edited name'}
        with self.assertRaises(exc.HTTPNotFound):
            edit_query_view(req)
        req.matchdict['id'] = query.id
        with self.assertRaises(exc.HTTPBadRequest):
            edit_query_view(req)
        req.json_body = {'query': 'query string'}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_query_view(req)
        req.json_body = {'name': 'Query2', 'query': 'query string', 'dashboard_id': dash.id}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_query_view(req)

        req.json_body = {'name': 'Edited name', 'query': 'query string', 'dashboard_id': dash.id,
                         'data_source_id': datasource.id}
        resp = edit_query_view(req)
        self.assertEqual(resp['name'], 'Edited name')
        self.assertEqual(resp['dashboard_id'], dash.id)

    def test_list_queries(self):
        datasource = DataSource(name='datasource')
        self.session.add(datasource)
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        dash2 = add_dashboard(self.session, 'Dash2', 'Dashboard')
        self.session.add(Query(name='Query', query='query string', dashboard_id=dash.id, data_source_id=datasource.id))
        self.session.add(Query(name='Query2', query='query string', dashboard_id=dash.id, data_source_id=datasource.id))
        self.session.add(Query(name='Query3', query='query', dashboard_id=dash2.id, data_source_id=datasource.id))

        req = dummy_request(self.session)
        req.params = {}
        resp = list_queries_view(req)
        self.assertEqual(len(resp), 3)

        req.params = {'dashboard_id': dash.id}
        resp = list_queries_view(req)
        self.assertEqual(len(resp), 2)

    def test_delete_query(self):
        datasource = DataSource(name='datasource')
        self.session.add(datasource)
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        query = Query(name='Query', query='query', dashboard_id=dash.id, data_source_id=datasource.id)
        self.session.add(query)
        req = dummy_request(self.session)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            delete_query_view(req)

        req.matchdict['id'] = query.id
        delete_query_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            delete_query_view(req)
