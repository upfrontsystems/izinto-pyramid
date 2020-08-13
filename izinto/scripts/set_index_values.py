""" Import active handlers and dogs """
import os
import sys
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config

from izinto.models import initialize_sql, Chart, Dashboard


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini#izinto-app")' % (cmd))
    sys.exit(1)


def main(argv=sys.argv):
    """ Set ordered values on index columns that are null """
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options={})
    engine = engine_from_config(settings, 'sqlalchemy.')
    session = initialize_sql(engine)

    # fix null index in charts
    null_index_charts = session.query(Chart).filter(Chart.index == None).order_by(Chart.dashboard_id).all()
    for chart in null_index_charts:
        index = session.query(Chart).filter(Chart.index != None, Chart.dashboard_id == chart.dashboard_id).count()
        chart.index = index
        print("Chart %s in dashboard %s index set to %s." % (chart.title, chart.dashboard.title, index))

    # fix null index in dashboards
    null_index_dashboards = session.query(Dashboard).filter(Dashboard.index == None) \
        .order_by(Dashboard.collection_id).all()
    for dash in null_index_dashboards:
        index = session.query(Dashboard).filter(Dashboard.index != None,
                                                Dashboard.collection_id == dash.collection_id).count()
        dash.index = index
        print("Dashboard %s in collection %s index set to %s." % (dash.title, dash.collection_id, index))

    transaction.commit()
