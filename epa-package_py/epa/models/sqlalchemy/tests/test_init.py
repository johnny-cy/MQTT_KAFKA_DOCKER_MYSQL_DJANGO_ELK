#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import sqlalchemy

from epa.models.sqlalchemy import sqlalchemy_db
from epa.models.sqlalchemy import SQLAlchemyProperties


class TestSQLAlchemy(unittest.TestCase):
    def test_default_mysql_engine(self):
        engine = sqlalchemy_db.engine
        self.assertIsInstance(engine, sqlalchemy.engine.Engine)
        self.assertEqual(engine.name, "mysql")


class TestCustomSQLAlchemy(unittest.TestCase):
    def setUp(self):
        db_dialect = "sqlite:///:memory:"
        self.db = SQLAlchemyProperties(db_dialect)

    def test_engine_exist(self):
        engine = self.db.engine
        self.assertIsInstance(engine, sqlalchemy.engine.Engine)
        self.assertEqual(engine.name, "sqlite")


if __name__ == '__main__':
    unittest.main()
