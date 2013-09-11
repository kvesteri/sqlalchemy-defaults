# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy import Boolean, Integer, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import false, true

from sqlalchemy_defaults import Column, make_lazy_configured


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_defaults_test'
        )
        self.Model = declarative_base()

        self.create_models(**self.column_options)
        sa.orm.configure_mappers()
        self.columns = self.User.__table__.c
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_models(self, **options):
        class User(self.Model):
            __tablename__ = 'user'
            __lazy_options__ = options

            id = Column(Integer, primary_key=True)
            name = Column(Unicode(255))
            age = Column(Integer, info={'min': 13, 'max': 120}, default=16)
            is_active = Column(Boolean)
            nullable_boolean = Column(Boolean, nullable=True)
            is_admin = Column(Boolean, default=True)
            hobbies = Column(Unicode(255), default=u'football')
            favorite_hobbies = Column(Unicode(255), default=lambda ctx: (
                ctx.current_parameters['hobbies']
                if ctx.current_parameters['hobbies'] is not None
                else u'football'
            ))
            favorite_buddy = Column(Unicode(255), default=u'Örrimörri')
            created_at = Column(sa.DateTime, info={'auto_now': True})
            description = Column(sa.UnicodeText)

        class Article(self.Model):
            __tablename__ = 'article'
            __lazy_options__ = options
            id = Column(Integer, primary_key=True)
            name = Column(Unicode(255))
            author_id = Column(Integer, sa.ForeignKey(User.id))

        self.User = User
        self.Article = Article


make_lazy_configured(
    sa.orm.mapper
)


class TestLazyConfigurableDefaults(TestCase):
    column_options = {}

    def test_creates_min_and_max_check_constraints(self):
        from sqlalchemy.schema import CreateTable

        sql = unicode(CreateTable(self.User.__table__).compile(self.engine))
        assert 'CHECK (age >= 13)' in sql
        assert 'CHECK (age <= 120)' in sql

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

    def test_strings_not_nullable(self):
        assert self.columns.name.nullable is False
        assert self.columns.description.nullable is False

    def test_assigns_string_server_defaults(self):
        assert self.columns.hobbies.server_default.arg == u'football'

    def test_doesnt_assign_string_server_defaults_for_callables(self):
        assert self.columns.favorite_hobbies.server_default is None

    def test_assigns_int_server_defaults(self):
        assert self.columns.age.server_default.arg == '16'

    def test_assigns_auto_now_defaults(self):
        created_at = self.columns.created_at
        assert created_at.default
        assert (
            created_at.server_default.arg.__class__ ==
            sa.func.now().__class__
        )

    def test_assigns_indexes_for_foreign_keys(self):
        assert self.Article.__table__.c.author_id.index is True


class TestLazyConfigurableOptionOverriding(TestCase):
    column_options = {
        'min_max_check_constraints': False,
        'string_defaults': False,
        'integer_defaults': False,
        'boolean_defaults': False,
        'auto_now': False
    }

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
