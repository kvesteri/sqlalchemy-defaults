# -*- coding: utf-8 -*-
import pytest
import six
import sqlalchemy as sa

from sqlalchemy_defaults import Column


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestLazyConfigurableDefaults(object):

    @pytest.fixture
    def User(self, Base, lazy_options):

        class User(Base):
            __tablename__ = 'user'
            __lazy_options__ = lazy_options

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

        return User

    @pytest.fixture
    def Article(self, Base, User, lazy_options):

        class Article(Base):
            __tablename__ = 'article'
            __lazy_options__ = lazy_options
            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            author_id = Column(sa.Integer, sa.ForeignKey(User.id))

        return Article

    @pytest.fixture
    def models(self, User, Article):
        return [User, Article]

    def test_creates_min_and_max_check_constraints(self, User, engine):
        from sqlalchemy.schema import CreateTable

        sql = six.text_type(
            CreateTable(User.__table__).compile(engine)
        )
        assert 'CHECK (age >= 13)' in sql
        assert 'CHECK (age <= 120)' in sql

    def test_assigns_int_server_defaults(self, User):
        assert User.__table__.c.age.server_default.arg == '16'

    def test_assigns_indexes_for_foreign_keys(self, Article):
        assert Article.__table__.c.author_id.index is True

    def test_insert(self, User, session):
        user = User(name=u'Someone', description=u'Some description')
        session.add(user)
        session.commit()


@pytest.mark.usefixtures('lazy_configured', 'Session')
class TestLazyConfigurableOptionOverriding(object):
    @pytest.fixture
    def lazy_options(self):
        return {
            'min_max_check_constraints': False,
            'string_defaults': False,
            'numeric_defaults': False,
            'boolean_defaults': False,
            'auto_now': False
        }

    @pytest.fixture
    def User(self, Base, lazy_options):
        class User(Base):
            __tablename__ = 'user'
            __lazy_options__ = lazy_options

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
        return User

    @pytest.fixture
    def Article(self, Base, User, lazy_options):
        class Article(Base):
            __tablename__ = 'article'
            __lazy_options__ = lazy_options
            id = Column(sa.Integer, primary_key=True)
            name = Column(sa.Unicode(255))
            author_id = Column(sa.Integer, sa.ForeignKey(User.id))
        return Article

    @pytest.fixture
    def models(self, User, Article):
        return [User, Article]

    def test_check_constraints(self, User, engine):
        from sqlalchemy.schema import CreateTable

        sql = str(CreateTable(User.__table__).compile(engine))
        assert 'CHECK (age >= 13)' not in sql
        assert 'CHECK (age <= 120)' not in sql

    def test_booleans_defaults(self, User):
        assert User.__table__.c.is_active.nullable is False
        assert User.__table__.c.is_active.default is None

        is_admin = User.__table__.c.is_admin
        is_active = User.__table__.c.is_active
        assert is_admin.server_default is None
        assert is_active.server_default is None

    def test_string_defaults(self, User):
        assert User.__table__.c.hobbies.server_default is None

    def test_integer_defaults(self, User):
        assert User.__table__.c.age.server_default is None

    def test_auto_now(self, User):
        created_at = User.__table__.c.created_at
        assert not created_at.default
        assert not created_at.server_default
