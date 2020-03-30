from izinto.tests import BaseTest, add_dashboard
from izinto.models.chart import Chart
from izinto.models.data_source import DataSource


class TestChartModel(BaseTest):
    """
    Test chart model
    """

    def test_add_chart(self):
        """ Test add a chart """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        chart = Chart(title="Temperature",
                      unit="°C",
                      color="blue",
                      decimals=2,
                      type="line",
                      query="select mean(temp)",
                      dashboard_id=dashboard.id,
                      data_source_id=data_source.id,
                      labels='Min,Max,Avg',
                      index=0,
                      min=0,
                      max=50,
                      height=200,
                      )
        self.session.add(chart)
        self.session.flush()
        self.assertIsNotNone(chart.id)
        self.assertEqual(chart.title, 'Temperature')
        self.assertEqual(chart.unit, '°C')
        self.assertEqual(chart.color, 'blue')
        self.assertEqual(chart.type, 'line')
        self.assertEqual(chart.query, 'select mean(temp)')
        self.assertEqual(chart.dashboard, dashboard)
        self.assertEqual(chart.data_source, data_source)
        self.assertEqual(chart.index, 0)
        self.assertEqual(chart.min, 0)
        self.assertEqual(chart.labels, 'Min,Max,Avg')
        self.assertEqual(chart.max, 50)
        self.assertEqual(chart.height, 200)

    def test_as_dict(self):
        """ Test as_dict method """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        chart = Chart(title="Temperature",
                      unit="°C",
                      color="blue",
                      decimals=2,
                      type="line",
                      query="select mean(temp)",
                      dashboard_id=dashboard.id,
                      data_source_id=data_source.id,
                      index=0,
                      labels='Min,Max,Avg',
                      min=0,
                      max=50,
                      height=200,
                      )
        self.session.add(chart)
        self.session.flush()
        self.assertEqual(chart.as_dict(), {
            'id': chart.id,
            'title': "Temperature",
            'unit': "°C",
            'color': "blue",
            'decimals': 2,
            'group_by': [],
            'type': "line",
            'query': "select mean(temp)",
            'dashboard_id': dashboard.id,
            'data_source_id': data_source.id,
            'data_source': data_source.as_dict(),
            'index': 0,
            'labels': 'Min,Max,Avg',
            'min': 0,
            'max': 50,
            'height': 200
        })

    def test__repr__(self):
        """ Test __repr__ method """
