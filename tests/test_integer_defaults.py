# -*- coding: utf-8 -*-
import sqlalchemy as sa

from sqlalchemy_defaults import Column
from tests import TestCase


class TestIntegerDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            age = Column(sa.Integer, info={'min': 13, 'max': 120}, default=16)

        self.User = User

    def test_assigns_int_server_defaults(self):
        assert self.columns.age.server_default.arg == '16'


class TestIntegerWithSequence(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, sa.Sequence('id_seq'), primary_key=True)

        self.User = User

    def test_assigns_int_server_defaults(self):
        assert isinstance(self.columns.id.default, sa.Sequence)
