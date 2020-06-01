import pyramid.httpexceptions as exc

from izinto.models import Dashboard, DataSource
from izinto.tests import BaseTest, dummy_request
from izinto.views.script import (create_script_view, get_script_view, edit_script_view, list_scripts_view,
                                 delete_script_view, reorder_script_view)


class TestScriptViews(BaseTest):

    def test_create_script(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        self.session.flush()

        # Test error validation
        # title and content fields are missing
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'dashboard_id': dashboard.id
            }
            create_script_view(req)

        # content field is missing
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'title': 'Title',
                'dashboard_id':  dashboard.id
            }
            create_script_view(req)

        req.json_body = {
            'title': 'D3 Bar Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }

        script = create_script_view(req)
        self.assertIsNotNone(script.get('id'))
        self.assertEqual(script['title'], 'D3 Bar Chart')
        self.assertEqual(script['content'], 'import d3')
        self.assertEqual(script['index'], 0)

        req.json_body = {
            'title': 'D3 Line Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script2 = create_script_view(req)
        self.assertEqual(script2['title'], 'D3 Line Chart')
        self.assertEqual(script2['index'], 1)

    def test_get_script(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        self.session.flush()

        # no id set on request
        with self.assertRaises(exc.HTTPBadRequest):
            get_script_view(req)

        # no record found
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 10}
            get_script_view(req)

        req.json_body = {
            'title': 'D3 Line Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script = create_script_view(req)
        script_id = script['id']
        req.matchdict = {'id': script_id}

        script = get_script_view(req)
        self.assertEqual(script_id, script['id'])

    def test_edit_script(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        self.session.flush()

        req.json_body = {
            'title': 'D3 Line Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }

        script = create_script_view(req)
        script_id = script['id']

        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_script_view(req)
        # need title and content
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict = {'id': script_id}
            edit_script_view(req)
        # need content
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict = {'id': script_id}
            req.json_body = {'title': 'Title'}
            edit_script_view(req)
        # record not found
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 10}
            req.json_body = {'title': 'Title', 'content': 'import d3'}
            edit_script_view(req)

        req.matchdict = {'id': script_id}
        script_content = "import d3; d3.selectAll(body).append('h1').text('hallo!')"
        req.json_body = {
            'title': 'D3 Bar Chart',
            'dashboard_id': dashboard.id,
            'content': script_content,
        }
        edit_script_view(req)

        script = get_script_view(req)
        self.assertEqual(script['title'], 'D3 Bar Chart')
        self.assertEqual(script['content'], script_content)

    def test_list_scripts(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        dashboard2 = Dashboard(title='Dashboard Title 2')
        self.session.add(dashboard2)
        self.session.flush()

        req.json_body = {
            'title': 'D3 Line Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script = create_script_view(req)

        req.json_body = {
            'title': 'D3 Bar Chart',
            'dashboard_id': dashboard2.id,
            'content': 'import d3',
        }
        create_script_view(req)

        req = dummy_request(self.session)
        req.params = {}
        scripts = list_scripts_view(req)
        self.assertEqual(len(scripts), 2)

        req.params = {'dashboard_id': dashboard.id}
        scripts = list_scripts_view(req)
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0]['id'], script['id'])

    def test_delete_script(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        self.session.flush()

        req.json_body = {
            'title': 'D3 Bar Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script = create_script_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 0}
            delete_script_view(req)

        req.matchdict = {"id": script['id']}
        delete_script_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            get_script_view(req)

    def test_reorder_scripts(self):
        req = dummy_request(self.session)
        dashboard = Dashboard(title='Dashboard Title')
        self.session.add(dashboard)
        data_source = DataSource(name='Datasource')
        self.session.add(data_source)
        self.session.flush()

        req.json_body = {
            'title': 'D3 Bar Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script1 = create_script_view(req)
        req.json_body = {
            'title': 'D3 Line Chart',
            'dashboard_id': dashboard.id,
            'content': 'import d3',
        }
        script2 = create_script_view(req)

        # need record id
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {'dashboard_id': dashboard.id}
            reorder_script_view(req)
        # need index of new position
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict = {'id': 10}
            req.json_body = {'dashboard_id': dashboard.id}
            reorder_script_view(req)
        # record not found
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 10}
            req.json_body = {'dashboard_id': dashboard.id,
                             'index': 1}
            reorder_script_view(req)

        req = dummy_request(self.session)
        req.params = {}

        scripts = list_scripts_view(req)
        self.assertEqual(scripts[0]['id'], script1['id'])

        req.matchdict = {'id': script1['id']}
        req.json_body = {'dashboard_id': dashboard.id,
                         'index': 1}
        reorder_script_view(req)
        scripts = list_scripts_view(req)
        self.assertEqual(scripts[0]['id'], script2['id'])
        self.assertEqual(scripts[1]['id'], script1['id'])
        self.assertEqual(scripts[0]['index'], 0)
        self.assertEqual(scripts[1]['index'], 1)

