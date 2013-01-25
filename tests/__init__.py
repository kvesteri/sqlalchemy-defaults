from sqlalchemy import Column, Boolean, Integer, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_defaults import LazyConfigured


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')
        self.Model = declarative_base()

        self.User = self.create_user_model(**self.column_options)
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_account_model(self, **options):
        class User(self.Model, LazyConfigured):
            __tablename__ = 'posts'

            id = Column(Integer, primary_key=True)
            name = Column(Unicode(255))
            age = Column(Integer, info={'min': 13, 'max': 120})
            is_active = Column(Boolean)

            __column_options__ = options

            def __init__(self, title):
                self.title = title

        return User


class TestLazyConfigurable(TestCase):
    column_options = {}

    def test_creates_min_and_max_check_constraints(self):
        from sqlalchemy.schema import CreateTable

        print CreateTable(self.User)


