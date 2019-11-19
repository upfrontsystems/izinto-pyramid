izinto
======

Getting Started
---------------

- Change directory into cloned directory:

    cd izinto-pyramid

- Create a Python virtual environment.

    python3 -m venv venv

- Upgrade packaging tools.

    venv/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    venv/bin/pip install -e ".[testing]"

- Create Postgres database:

    CREATE USER izinto WITH PASSWORD 'izinto';
    CREATE DATABASE izinto OWNER izinto;

- Initialize and upgrade the database using Alembic.

    - Upgrade to latest revision.

        venv/bin/alembic upgrade head

- Load default data into the database using a script.

    venv/bin/initialize_izinto_db development.ini

- Run your project's tests.

    venv/bin/pytest

- Run your project.

    venv/bin/pserve development.ini
