# -*- coding: utf-8 -*-
import six
import sqlalchemy as sa

from sqlalchemy_defaults import Column
from tests import TestCase


class TestLazyConfigurableDefaults(TestCase):
    column_options = {}

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            age = Column(sa.Integer, info={'min': 13, 'max': 120}, default=16)
            is_active = Column(sa.Boolean)
            nullable_boolean = Column(sa.Boolean, nullable=True)
            is_admin = Column(sa.Boolean, default=True)
            hobbies = Column(sa.Unicode(255), default=u'football')
            favorite_hobbies = Column(sa.Unicode(255), default=lambda ctx: (
                ctx.current_parameters['hobbies']
                if ctx.current_parameters['hobbies'] is not None
                else u'football'
            ))
            favorite_buddy = Column(sa.Unicode(255), default=u'Örrimörri')
            description = Column(sa.UnicodeText)

        class Article(self.Model):
            __tablename__ = 'article'
            __lazy_options__ = options
            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            author_id = Column(sa.Integer, sa.ForeignKey(User.id))

        self.User = User
        self.Article = Article

    def test_creates_min_and_max_check_constraints(self):
        from sqlalchemy.schema import CreateTable

        sql = six.text_type(
            CreateTable(self.User.__table__).compile(self.engine)
        )
        assert 'CHECK (age >= 13)' in sql
        assert 'CHECK (age <= 120)' in sql

    def test_assigns_int_server_defaults(self):
        assert self.columns.age.server_default.arg == '16'

    def test_assigns_indexes_for_foreign_keys(self):
        assert self.Article.__table__.c.author_id.index is True

    def test_insert(self):
        user = self.User(name=u'Someone', description=u'Some description')
        self.session.add(user)
        self.session.commit()


class TestLazyConfigurableOptionOverriding(TestCase):
    column_options = {
        'min_max_check_constraints': False,
        'string_defaults': False,
        'numeric_defaults': False,
        'boolean_defaults': False,
        'auto_now': False
    }

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            age = Column(sa.Integer, info={'min': 13, 'max': 120}, default=16)
            is_active = Column(sa.Boolean)
            nullable_boolean = Column(sa.Boolean, nullable=True)
            is_admin = Column(sa.Boolean, default=True)
            hobbies = Column(sa.Unicode(255), default=u'football')
            favorite_hobbies = Column(sa.Unicode(255), default=lambda ctx: (
                ctx.current_parameters['hobbies']
                if ctx.current_parameters['hobbies'] is not None
                else u'football'
            ))
            favorite_buddy = Column(sa.Unicode(255), default=u'Örrimörri')
            created_at = Column(sa.DateTime, info={'auto_now': True})
            description = Column(sa.UnicodeText)

        class Article(self.Model):
            __tablename__ = 'article'
            __lazy_options__ = options
            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            author_id = Column(sa.Integer, sa.ForeignKey(User.id))

        self.User = User
        self.Article = Article

    def test_check_constraints(self):
        from sqlalchemy.schema import CreateTable

        sql = str(CreateTable(self.User.__table__).compile(self.engine))
        assert 'CHECK (age >= 13)' not in sql
        assert 'CHECK (age <= 120)' not in sql

    def test_booleans_defaults(self):
        assert self.columns.is_active.nullable is False
        assert self.columns.is_active.default is None

        is_admin = self.columns.is_admin
        is_active = self.columns.is_active
        assert is_admin.server_default is None
        assert is_active.server_default is None

    def test_string_defaults(self):
        assert self.columns.hobbies.server_default is None

    def test_integer_defaults(self):
        assert self.columns.age.server_default is None

    def test_auto_now(self):
        created_at = self.columns.created_at
        assert not created_at.default
        assert not created_at.server_default
