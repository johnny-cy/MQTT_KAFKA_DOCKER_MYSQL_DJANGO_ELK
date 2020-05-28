#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, text, desc
from sqlalchemy.dialects.mysql import insert

from epa.logging import get_logger
from epa.models._data_io import DataIOHandler, DataResultProxy, DataIOWriteError

db_dialect = os.environ.get("SQLALCHEMY_DB_DIALECT")
if not db_dialect:
    try:
        from local_settings import SQLALCHEMY_DB_DIALECT
        db_dialect = SQLALCHEMY_DB_DIALECT
    except ModuleNotFoundError:
        if not db_dialect:
            MYSQL_ADDRESS = "mysql"
            MYSQL_DB = "epa"
            MYSQL_USER = "epa"
            MYSQL_PASSWORD = "epa"
            MYSQL_CONNECTION_DIALECT = (
                f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}/"
                f"{MYSQL_DB}?charset=utf8mb4"
            )
            SQLALCHEMY_DB_DIALECT = MYSQL_CONNECTION_DIALECT
            db_dialect = SQLALCHEMY_DB_DIALECT


logger = get_logger(__name__)

_echo = True if os.environ.get("DEBUG_SQLALCHEMY_ECHO") else False

engine = create_engine(db_dialect, encoding='utf8',
        pool_pre_ping=True, echo=_echo)
""" sqlalchemy.engine.Engine : SQLAlchemy engine
"""

DeclarativeBase = declarative_base(bind=engine)
""" sqlalchemy.ext.declarative.declarative_base : declarative class base
"""

Session = sessionmaker(bind=engine)
""" sqlalchemy.orm.session.Session : SQLAlchemy session factory
"""


def create_all_tables():
    DeclarativeBase.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SQLSourceMixin(object):
    def save(self):
        with session_scope() as session:
            session.merge(self)


class SQLAlchemyResultProxy(DataResultProxy):
    def __init__(self, data_cls, db_cls, sql_statement, params):
        self.data_cls = data_cls
        self.db_cls = db_cls
        self.sql_statement = sql_statement
        self.params = params

        # self.sql_statement.stmt.bindparams(**params)

    def get_one(self):
        conn = engine.connect()
        try:
            result = conn.execute(self.sql_statement, self.params).fetchone()
            return dict(result) if result else None
        except Exception as err:
            logger.exception(err)
        finally:
            conn.close()

    def get_object(self):
        one = self.get_one()
        return self.data_cls(**one) if one else None

    def as_list(self):
        conn = engine.connect()
        try:
            result = conn.execute(self.sql_statement, self.params)
            return [dict(r) for r in result.fetchall()]
        except Exception as err:
            logger.exception(err)
        finally:
            conn.close()

    def as_objects(self):
        result = self.as_list()
        return [self.data_cls(**x) for x in result]

    def as_df(self):
        return pd.read_sql(self.sql_statement, con=engine, params=self.params)

    def as_stream(self, batch_size=1000):
        conn = engine.connect()
        try:
            result_proxy = conn.execute(self.sql_statement, self.params)
            ret = []
            for idx, row in enumerate(result_proxy, start=1):
                ret.append(dict(row))
                if len(ret) % batch_size == 0:
                    yield DataResultProxy(self.data_cls, ret)
                    ret = []
            if ret:
                yield DataResultProxy(self.data_cls, ret)
        except Exception as err:
            logger.exception(err)
        finally:
            conn.close()


class SQLAlchemyHandler(DataIOHandler):
    def __init__(self, data_cls, db_cls):
        self.data_cls = data_cls
        self.db_cls = db_cls

    def read(self, fields=[], where=[], sort=[], limit=None, offset=None, **kwargs):
        cls = self.db_cls
        if fields:
            stmt = select([getattr(cls, c) for c in fields])
        else:
            stmt = select([cls])

        for w in where:
            if isinstance(w, str):
                w = text(w)
            stmt = stmt.where(w)

        for s in sort:
            if s[0] == "-":
                stmt = stmt.order_by(desc(s[1:]))
            else:
                stmt = stmt.order_by(s)

        if limit:
            stmt = stmt.limit(limit)

        if offset:
            stmt = stmt.offset(offset)

        return SQLAlchemyResultProxy(self.data_cls, self.db_cls, stmt, kwargs)

    def write(self, data, batch_size=1000):
        if isinstance(data, pd.DataFrame):
            self.write_df(data, batch_size)
        elif isinstance(data, list):
            self.write_list(data, batch_size)
        else:
            self.write([data])

    def write_list(self, data, batch_size=1000):
        if engine.name == "mysql":
            # NOTE: objects in data array has to have same keys
            success, exception = self._insert_list_on_duplicate_key(
                self.db_cls, data, batch_size)
            if not success:
                raise exception
        else:
            with session_scope() as session:
                for idx, x in enumerate(data):
                    obj = self.db_cls(**x)
                    session.merge(obj)
                    if idx % batch_size == 0:
                        session.commit()

    def write_df(self, df, batch_size=1000):
        if engine.name == "mysql":
            success, exception = self._insert_df_on_duplicate_key(
                self.db_cls, df, batch_size)
            if not success:
                raise exception
        else:
            # default, using session.merge
            with session_scope() as session:
                for idx, x in df.iterrows():
                    obj = self.db_cls(**(x.to_dict()))
                    session.merge(obj)
                    if idx % batch_size == 0:
                        session.commit()

    def _insert_list_on_duplicate_key(self, cls, data, batch_size):
        success = True
        exception = DataIOWriteError()
        for i in range(0, len(data), batch_size):
            chunk = data[i: i + batch_size]  # out-of-bound is safe in python3
            s, e = self._do_insert_on_duplicate_key(cls, chunk)
            success &= s
            exception.combine(e)

        return success, exception

    def _insert_df_on_duplicate_key(self, cls, df, batch_size):
        success = True
        exception = DataIOWriteError()
        for i in range(0, len(df), batch_size):
            _df = df.iloc[i: i + batch_size]
            chunk = _df.where(pd.notnull(_df), None)\
                       .to_dict(orient="records")
            s, e = self._do_insert_on_duplicate_key(cls, chunk)
            success &= s
            exception.combine(e)

        return success, exception

    def _do_insert_on_duplicate_key(self, cls, data):
        try:
            self._do_mysql_insert_on_duplicate_key(cls, data)
            return True, DataIOWriteError()   # no error
        except DataIOWriteError as err:
            if len(data) == 1:
                return False, err
            else:
                helf = int(len(data) / 2)
                s1, e1 = self._do_insert_on_duplicate_key(cls, data[:helf])
                s2, e2 = self._do_insert_on_duplicate_key(cls, data[helf:])
                return s1 & s2, e1.combine(e2)

    def _do_mysql_insert_on_duplicate_key(self, cls, data):
        # NOTE: only update columns of first object
        columns = data[0].keys()
        stmt = insert(cls.__table__).values(data)
        do_update_stmt = stmt.on_duplicate_key_update(
            **{c: getattr(stmt.inserted, c) for c in columns}
        )
        conn = engine.connect()
        try:
            result = conn.execute(do_update_stmt)
            return result.rowcount
        except Exception as err:
            raise DataIOWriteError(err)
        finally:
            conn.close()

