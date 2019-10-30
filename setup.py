import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'alembic==1.0.10',
    'plaster_pastedeploy==0.7',
    'postgres==2.2.2',
    'PyJWT==1.7.1',
    'pyramid==1.10.4',
    'pyramid_jinja2==2.8',
    'pyramid_debugtoolbar==4.5',
    'pyramid_retry',
    'pyramid_tm==2.2.1',
    'SQLAlchemy==1.3.3',
    'transaction==2.4.0',
    'waitress==1.3.0',
    'zope.sqlalchemy==1.1',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest >= 3.7.4',
    'pytest-cov',
]

setup(
    name='izinto',
    version='0.0',
    description='izinto',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = izinto:main',
        ],
        'console_scripts': [
            'initialize_izinto_db=izinto.scripts.initialize_db:main',
        ],
    },
)
