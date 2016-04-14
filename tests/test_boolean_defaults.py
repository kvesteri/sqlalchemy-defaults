# -*- coding: utf-8 -*-
import pytest
import sqlalchemy as sa
from sqlalchemy.sql.expression import false, true

from sqlalchemy_defaults import Column


@pytest.fixture
def User(Base, lazy_options):
    class User(Base):
        __tablename__ = 'user'
        __lazy_options__ = lazy_options

        id = Column(sa.Integer, primary_key=True)
        is_active = Column(sa.Boolean)
        nullable_boolean = Column(sa.Boolean, nullable=True)
        is_admin = Column(sa.Boolean, default=True)
    return User


@pytest.fixture
def models(User):
    return [User]


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestBooleanDefaults(object):

    def test_booleans_not_nullable_by_default(self, User):
        assert User.__table__.c.is_active.nullable is False

    def test_supports_nullable_booleans(self, User):
        assert User.__table__.c.nullable_boolean.nullable

    def test_booleans_false(self, User):
        assert User.__table__.c.is_active.default.arg is False

    def test_assigns_boolean_server_defaults(self, User):
        is_admin = User.__table__.c.is_admin
        is_active = User.__table__.c.is_active
        assert is_admin.default.arg is True

        assert is_admin.server_default.arg.__class__ == true().__class__
        assert is_active.server_default.arg.__class__ == false().__class__
