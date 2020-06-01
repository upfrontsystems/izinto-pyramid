from izinto.models.data_source import DataSource
from izinto.models.single_stat import SingleStat
from izinto.tests import BaseTest, add_dashboard


class TestSingleStatModel(BaseTest):
    """
    Test single_stat model
    """

    def test_add_single_stat(self):
        """ Test add a single_stat """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        single_stat = SingleStat(title='Single stat',
                                 query='query',
                                 decimals=2,
                                 format='{}',
                                 thresholds='[1,2]',
                                 colors='[#000,#333,#fff]',
                                 dashboard_id=dashboard.id,
                                 data_source_id=data_source.id)
        self.session.add(single_stat)
        self.session.flush()
        self.assertIsNotNone(single_stat.id)
        self.assertEqual(single_stat.title, 'Single stat')
        self.assertEqual(single_stat.decimals, 2)
        self.assertEqual(single_stat.query, 'query')
        self.assertEqual(single_stat.dashboard, dashboard)
        self.assertEqual(single_stat.data_source, data_source)

    def test_as_dict(self):
        """ Test as_dict method """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        single_stat = SingleStat(title='Single stat',
                                 query='query',
                                 decimals=0,
                                 format='{}',
                                 thresholds='[1]',
                                 colors='[#000,#fff]',
                                 dashboard_id=dashboard.id,
                                 data_source_id=data_source.id)
        self.session.add(single_stat)
        self.session.flush()
        self.assertEqual(single_stat.as_dict()['title'], 'Single stat')
        self.assertEqual(single_stat.as_dict()['data_source'], data_source.as_dict())

    def test__repr__(self):
        """ Test __repr__ method """
        dashboard = add_dashboard(self.session, 'Dashboard')
        data_source = DataSource(name='ds')
        self.session.add(data_source)
        self.session.flush()
        single_stat = SingleStat(title='Single stat',
                                 query='query',
                                 decimals=0,
                                 format='{}',
                                 thresholds='[1]',
                                 colors='[#000,#fff]',
                                 dashboard_id=dashboard.id,
                                 data_source_id=data_source.id)
        self.session.add(single_stat)
        self.session.flush()

        self.assertEqual(single_stat.__repr__(), 'SingleStat<id: %s, title: "Single stat">' % single_stat.id)
