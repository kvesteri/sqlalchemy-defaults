# -*- coding: utf-8 -*-
import sqlalchemy as sa

from sqlalchemy_defaults import Column
from tests import TestCase


class TestNumericDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class Account(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            balance = Column(
                sa.Numeric,
                min=0,
                max=2000,
                default=100
            )

        self.Account = Account
        self.columns = Account.__table__.c

    def test_assigns_real_server_defaults(self):
        assert self.columns.balance.server_default.arg == '100'
