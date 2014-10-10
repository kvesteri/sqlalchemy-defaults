# -*- coding: utf-8 -*-
from datetime import date, datetime
import sqlalchemy as sa

from sqlalchemy_defaults import Column
from tests import TestCase


class TestDateTimeDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            created_at = Column(sa.DateTime, auto_now=True)
            fav_day = Column(
                sa.Date, min=date(2000, 1, 1), max=date(2099, 1, 1)
            )

        self.User = User

    def test_autonow(self):
        column = self.User.created_at
        assert isinstance(column.default.arg(column), datetime)
        assert (
            column.server_default.arg.__class__ == sa.func.now().__class__
        )
