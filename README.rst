SQLAlchemy-Defaults
=====================

Smart SQLAlchemy defaults for lazy guys, like me.

Running the tests
-----------------

You need PostgreSQL and MySQL installed to run the full test suite.

To run:
::
    $ pip install tox
    $ POSTGRESQL_DSN='postgresql://user@host:port/db' \
    MYSQL_DSN='mysql+pymysql://user@host:port/db' \
    tox


To type a bit less to run the tests you can save the command in a script:
::
    $ echo "POSTGRESQL_DSN='postgresql://user@host:port/db' \\ \\nMYSQL_DSN='mysql+pymysql://user@host:port/db' \\ \\ntox" > tox.sh
    $ chmod +x tox.sh
    $ ./tox.sh


Resources
---------

- `Documentation <https://sqlalchemy-defaults.readthedocs.io/>`_
- `Issue Tracker <http://github.com/kvesteri/sqlalchemy-defaults/issues>`_
- `Code <http://github.com/kvesteri/sqlalchemy-defaults/>`_
