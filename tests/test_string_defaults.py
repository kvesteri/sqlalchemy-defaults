# -*- coding: utf-8 -*-
import sqlalchemy as sa

from sqlalchemy_defaults import Column
from tests import TestCase


class TestStringDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

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

        self.User = User

    def test_strings_not_nullable(self):
        assert self.columns.name.nullable is False
        assert self.columns.description.nullable is False

    def test_assigns_string_server_defaults(self):
        assert self.columns.hobbies.server_default.arg == u'football'

    def test_override_server_default(self):
        assert self.columns.hobbies2.server_default.arg == u''

    def test_doesnt_assign_string_server_defaults_for_callables(self):
        assert self.columns.favorite_hobbies.server_default is None
