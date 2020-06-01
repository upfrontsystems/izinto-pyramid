from izinto.tests import BaseTest, add_dashboard
from izinto.models.script import Script
from izinto.models.data_source import DataSource


class TestScriptModel(BaseTest):
    """
    Test Script model
    """
    script_content = """
import d3;
d3.selectAll('body').append('h1').text('Test');
"""

    def test_script(self):
        """ Test adding a Script """
        dashboard = add_dashboard(self.session, 'Dashboard')
        script = Script(title="Forecast",
                        dashboard_id=dashboard.id,
                        content=self.script_content,
                        index=0)
        self.session.add(script)
        self.session.flush()
        self.assertIsNotNone(script.id)
        self.assertEqual(script.title, 'Forecast')
        self.assertEqual(script.dashboard, dashboard)
        self.assertEqual(script.index, 0)
        self.assertEqual(script.content, self.script_content)

    def test_as_dict(self):
        """ Test as_dict method """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        script = Script(title="Forecast",
                        dashboard_id=dashboard.id,
                        content=self.script_content,
                        index=0)
        self.session.add(script)
        self.session.flush()
        self.assertEqual(script.as_dict(), {
            'id': script.id,
            'title': "Forecast",
            'dashboard_id': dashboard.id,
            'index': 0,
            'content': self.script_content
        })

    def test__repr__(self):
        """ Test __repr__ method """
        script = Script(title="Forecast",
                        content=self.script_content,
                        index=0)
        self.session.add(script)
        self.session.flush()
        self.assertEqual(repr(script), "Script<id: %s, title: '%s'>" % (script.id, script.title))
