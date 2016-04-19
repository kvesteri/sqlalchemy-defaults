# -*- coding: utf-8 -*-
from datetime import date, datetime

import pytest
import sqlalchemy as sa

from sqlalchemy_defaults import Column


@pytest.fixture
def User(Base, lazy_options):

    class User(Base):
        __tablename__ = 'user'
        __lazy_options__ = lazy_options

        id = Column(sa.Integer, primary_key=True)
        created_at = Column(sa.DateTime, auto_now=True)
        fav_day = Column(
            sa.Date, min=date(2000, 1, 1), max=date(2099, 1, 1)
        )

    return User


@pytest.fixture
def models(User):
    return [User]


def supports_datetime_defaults(connection):
    return not (
        connection.engine.name == 'mysql' and
        connection.dialect.server_version_info < (5, 6, 5)
    )


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestDateTimeDefaults(object):
    @pytest.fixture
    def models(self, connection, User):
        if not supports_datetime_defaults(connection):
            return []
        return [User]

    def test_autonow(self, connection, User):
        if not supports_datetime_defaults(connection):
            pytest.skip('Not testing when MySQL is below version 5.6.5')
        column = User.created_at
        assert isinstance(column.default.arg(column), datetime)
        assert (
            column.server_default.arg.__class__ == sa.func.now().__class__
        )
