""" Check query range """
import os
import sys
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config

from izinto.models import initialize_sql, Chart


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini#izinto-app")' % (cmd))
    sys.exit(1)


def main(argv=sys.argv):
    """ check and update query range"""
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options={})
    engine = engine_from_config(settings, 'sqlalchemy.')
    session = initialize_sql(engine)

    # fix null index in charts
    for chart in session.query(Chart).all():
        if ":range:" not in chart.query:
            print("%s (%s) with no range in query %s" % (chart.title, chart.id, chart.query))
            chart.query = chart.query.replace('GROUP BY', 'AND :range: GROUP BY')
            chart.query = chart.query.replace('group by', 'AND :range: GROUP BY')

    transaction.commit()


if __name__ == '__main__':
    main()
