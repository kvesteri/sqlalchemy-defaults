# -*- coding: utf-8 -*-
import pytest
import sqlalchemy as sa

from sqlalchemy_defaults import Column


@pytest.fixture
def Account(Base, lazy_options):
    class Account(Base):
        __tablename__ = 'user'
        __lazy_options__ = lazy_options

        id = Column(sa.Integer, primary_key=True)
        balance = Column(
            sa.Numeric,
            min=0,
            max=2000,
            default=100
        )
    return Account


@pytest.fixture
def models(Account):
    return [Account]


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestNumericDefaults(object):

    @pytest.fixture
    def test_assigns_real_server_defaults(self, Account):
        assert Account.__table__.c.balance.server_default.arg == '100'
