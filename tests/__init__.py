# -*- coding: utf-8 -*-
import os
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_defaults import make_lazy_configured


make_lazy_configured(
    sa.orm.mapper
)


class TestCase(object):
    def get_dns_from_driver(self, driver):
        if driver == 'postgres':
            return 'postgres://postgres@localhost/sqlalchemy_defaults_test'
        elif driver == 'mysql':
            return 'mysql+pymysql://travis@localhost/sqlalchemy_defaults_test'
        elif driver == 'sqlite':
            return 'sqlite:///:memory:'
        else:
            raise Exception('Unknown driver given: %r' % driver)

    def setup_method(self, method):
        driver = os.environ.get('DB', 'sqlite')
        dns = self.get_dns_from_driver(driver)
        self.engine = create_engine(dns)
        self.Model = declarative_base()

        self.create_models(**self.column_options)
        sa.orm.configure_mappers()
        self.columns = self.User.__table__.c
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()
