import pyramid.httpexceptions as exc
from izinto.models import Variable
from izinto.tests import BaseTest, dummy_request, add_dashboard
from izinto.views.variable import (create_variable_view, get_variable_view, list_variables_view, delete_variable,
                                   edit_variable_view, delete_variable_view)


class TestVariableViews(BaseTest):

    def test_create_variable(self):
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        req = dummy_request(self.session)
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            create_variable_view(req)

        req.json_body = {'name': 'Variable',
                         'value': '5',
                         'dashboard_id': dash.id}
        variable = create_variable_view(req)

        self.assertIsNotNone(variable['id'])
        self.assertEqual(variable['name'], 'Variable')
        self.assertEqual(variable['dashboard_id'], dash.id)

    def test_get_variable(self):
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        variable = Variable(name='Variable', value='5', dashboard_id=dash.id)
        self.session.add(variable)
        self.session.flush()
        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            get_variable_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict['id'] = 100
            get_variable_view(req)

        req.matchdict['id'] = variable.id
        resp = get_variable_view(req)

        self.assertEqual(resp['id'], variable.id)
        self.assertEqual(resp['name'], 'Variable')

    def test_edit_variable(self):
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        variable = Variable(name='Variable', value='5', dashboard_id=dash.id)
        self.session.add(Variable(name='Variable2', value='5', dashboard_id=dash.id))
        self.session.add(variable)
        self.session.flush()

        req = dummy_request(self.session)
        req.matchdict = {}
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_variable_view(req)
        req.matchdict['id'] = 100
        req.json_body = {'name': 'Edited name'}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_variable_view(req)
        req.matchdict['id'] = 100
        req.json_body = {'value': '5'}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_variable_view(req)
        req.json_body = {'name': 'Edited name', 'value': '5', 'dashboard_id': dash.id}
        with self.assertRaises(exc.HTTPNotFound):
            edit_variable_view(req)

        req.matchdict['id'] = variable.id
        req.json_body = {'name': 'Variable2', 'value': '5', 'dashboard_id': dash.id}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_variable_view(req)

        req.json_body = {'name': 'Edited name', 'value': '5', 'dashboard_id': dash.id}
        resp = edit_variable_view(req)
        self.assertEqual(resp['name'], 'Edited name')
        self.assertEqual(resp['dashboard_id'], dash.id)

    def test_list_variables(self):
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        self.session.add(Variable(name='Variable', value='1', dashboard_id=dash.id))
        self.session.add(Variable(name='Variable2', value='2', dashboard_id=dash.id))
        self.session.add(Variable(name='Variable3', value='3', dashboard_id=dash.id))

        req = dummy_request(self.session)
        req.params = {}
        resp = list_variables_view(req)
        self.assertEqual(len(resp), 3)

        req.params = {'value': '1'}
        resp = list_variables_view(req)
        self.assertEqual(len(resp), 1)

    def test_delete_variable(self):
        dash = add_dashboard(self.session, 'Dash', 'Dashboard')
        variable = Variable(name='Variable', value='5', dashboard_id=dash.id)
        self.session.add(variable)
        req = dummy_request(self.session)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {'id': 100}
            delete_variable_view(req)

        req.matchdict['id'] = variable.id
        delete_variable_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            delete_variable_view(req)
