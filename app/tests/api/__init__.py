import os
import pytest
from app import create_app, db
from app.utils.db import create_tables
from app.utils.restaurant import fill_database_resturants, fill_database_dishes
from unittest import TestCase


class APITestCase(TestCase):

    @classmethod
    def _remove_sqlite_test_db(cls):
        try:
            os.remove(cls.app.config['SQLALCHEMY_DATABASE_FILE'])
        except OSError:
            pass

    @classmethod
    @pytest.fixture(autouse=True)
    def setupClass(cls):
        super(APITestCase, cls).setUpClass()
        cls.app = create_app('testing')
        cls.test_client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls._remove_sqlite_test_db()
        cls.app_context.push()
        create_tables(db)

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()
        cls._remove_sqlite_test_db()
        super(APITestCase, cls).tearDownClass()

    @classmethod
    def fill_db_resturants(cls):
        fill_database_resturants()
