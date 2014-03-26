# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.sql.expression import false, true

from sqlalchemy_defaults import Column
from tests import TestCase


class TestBooleanDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            is_active = Column(sa.Boolean)
            nullable_boolean = Column(sa.Boolean, nullable=True)
            is_admin = Column(sa.Boolean, default=True)

        self.User = User

    def test_booleans_not_nullable_by_default(self):
        assert self.columns.is_active.nullable is False

    def test_supports_nullable_booleans(self):
        assert self.columns.nullable_boolean.nullable

    def test_booleans_false(self):
        assert self.columns.is_active.default.arg is False

    def test_assigns_boolean_server_defaults(self):
        is_admin = self.columns.is_admin
        is_active = self.columns.is_active
        assert is_admin.default.arg is True

        assert is_admin.server_default.arg.__class__ == true().__class__
        assert is_active.server_default.arg.__class__ == false().__class__
