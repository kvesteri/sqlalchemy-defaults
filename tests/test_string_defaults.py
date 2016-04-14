# -*- coding: utf-8 -*-
import pytest
import sqlalchemy as sa

from sqlalchemy_defaults import Column


@pytest.fixture
def User(Base, lazy_options):
    class User(Base):
        __tablename__ = 'user'
        __lazy_options__ = lazy_options

        id = Column(sa.Integer, primary_key=True)
        name = Column(sa.Unicode(255))
        hobbies = Column(sa.Unicode(255), default=u'football')
        hobbies2 = Column(
            sa.Unicode(255), default=u'ice-hockey', server_default=u''
        )

        favorite_hobbies = Column(sa.Unicode(255), default=lambda ctx: (
            ctx.current_parameters['hobbies']
            if ctx.current_parameters['hobbies'] is not None
            else u'football'
        ))
        favorite_buddy = Column(sa.Unicode(255), default=u'Örrimörri')
        description = Column(sa.UnicodeText)
    return User


@pytest.fixture
def models(User):
    return [User]


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestStringDefaults(object):

    def test_strings_not_nullable(self, User):
        assert User.__table__.c.name.nullable is False
        assert User.__table__.c.description.nullable is False

    def test_assigns_string_server_defaults(self, User):
        assert User.__table__.c.hobbies.server_default.arg == u'football'

    def test_override_server_default(self, User):
        assert User.__table__.c.hobbies2.server_default.arg == u''

    def test_doesnt_assign_string_server_defaults_for_callables(self, User):
        assert User.__table__.c.favorite_hobbies.server_default is None
