# -*- coding: utf-8 -*-
import pytest
import sqlalchemy as sa

from sqlalchemy_defaults import Column


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestIntegerDefaults(object):

    @pytest.fixture
    def User(self, Base, lazy_options):
        class User(Base):
            __tablename__ = 'user'
            __lazy_options__ = lazy_options

            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            age = Column(sa.Integer, info={'min': 13, 'max': 120}, default=16)

        return User

    @pytest.fixture
    def models(self, User):
        return [User]

    def test_assigns_int_server_defaults(self, User):
        assert User.__table__.c.age.server_default.arg == '16'


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestIntegerWithSequence(object):

    @pytest.fixture
    def User(self, Base, lazy_options):
        class User(Base):
            __tablename__ = 'user'
            __lazy_options__ = lazy_options

            id = Column(sa.Integer, sa.Sequence('id_seq'), primary_key=True)

        return User

    @pytest.fixture
    def models(self, User):
        return [User]

    def test_assigns_int_server_defaults(self, User):
        assert isinstance(User.__table__.c.id.default, sa.Sequence)
