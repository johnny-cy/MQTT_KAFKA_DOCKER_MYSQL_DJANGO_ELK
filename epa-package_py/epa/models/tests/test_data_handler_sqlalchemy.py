#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from epa.models.sqlalchemy import DeclarativeBase, session_scope
from epa.models.iot import IoTDevice
from epa.models.sqlalchemy.iot import IoTDevice as IoTDeviceSQL
from epa.models._data_io import DataIOWriteError


def create_all_tables():
    drop_all_tables()
    DeclarativeBase.metadata.create_all()


def drop_all_tables():
    DeclarativeBase.metadata.drop_all()


class TestIoTDevice_SQLAlchemy(unittest.TestCase):
    def setUp(self):
        create_all_tables()

    def tearDown(self):
        drop_all_tables()

    def test_dataclass_as_dict(self):
        device_id = "xkL9dzlxvjew"
        x = IoTDevice(device_id=device_id)

        expected_result = {f: None for f in x.field_names}
        expected_result["device_id"] = device_id

        self.assertEqual(x.as_dict(), expected_result)

    def test_dataclass_as_tuple(self):
        device_id = "klELi092uDK"
        x = IoTDevice(device_id=device_id)

        expected_result = tuple(
            None if f != "device_id" else device_id for f in x.field_names)

        self.assertEqual(x.as_tuple(), expected_result)

    def test_dataclase_save_to_sqlalchemy_db(self):
        device_id = "xELP0d"
        x = IoTDevice(device_id=device_id)
        x.save()

        with session_scope() as session:
            ret = session.query(IoTDeviceSQL).one()
            self.assertEqual(ret.device_id, device_id)

    def test_data_io_handler(self):
        self.assertTrue(IoTDevice.sql is IoTDevice.mysql)
        self.assertTrue(IoTDevice.sql is IoTDevice.mariadb)
        self.assertTrue(IoTDevice.sql is IoTDevice.db)

    def test_data_io_handler_writing_list(self):
        data = [{"device_id": f"{i}"} for i in range(10)]
        IoTDevice.sql.write(data)

        with session_scope() as session:
            ret = session.query(IoTDeviceSQL).count()
            self.assertEqual(ret, 10)

    def test_data_io_handler_writing_df(self):
        data = [{"device_id": f"{i}"} for i in range(10)]
        df = pd.DataFrame(data)
        IoTDevice.sql.write(df)

        with session_scope() as session:
            ret = session.query(IoTDeviceSQL).count()
            self.assertEqual(ret, 10)

    def test_data_io_handler_writing_list_with_error(self):
        data = [{"device_id": f"{i}"} for i in range(10)]
        data[0]["device_id"] = None
        with self.assertRaises(DataIOWriteError):
            IoTDevice.sql.write(data)

        with session_scope() as session:
            ret = session.query(IoTDeviceSQL).count()
            self.assertEqual(ret, 9)

    def test_data_io_handler_writing_df_with_error(self):
        data = [{"device_id": f"{i}"} for i in range(10)]
        data[2]["device_id"] = None
        data[9]["device_id"] = None
        df = pd.DataFrame(data)
        with self.assertRaises(DataIOWriteError):
            IoTDevice.sql.write(df)

        with session_scope() as session:
            ret = session.query(IoTDeviceSQL).count()
            self.assertEqual(ret, 8)


class TestIoTDevice_DataIOHander_List(unittest.TestCase):
    def setUp(self):
        create_all_tables()
        self.data = [
            {"device_id": "1", "name": "name01", "desc": "desc01"},
            {"device_id": "2", "name": "name02", "desc": "desc02"},
            {"device_id": "3", "name": "name03", "desc": "desc03"},
            {"device_id": "4", "name": "name101", "desc": "desc04"},
            {"device_id": "5", "name": "name101", "desc": "desc05"},
        ]
        IoTDevice.sql.write(self.data)

    def tearDown(self):
        drop_all_tables()

    def test_data_io_handler_read_all(self):
        ret = IoTDevice.sql.read().as_list()
        self.assertEqual(len(ret), 5)
        for row in ret:
            self.assertTrue("device_id" in row)
            self.assertTrue("name" in row)
            self.assertTrue("desc" in row)

    def test_data_io_handler_read_with_fields(self):
        ret = IoTDevice.sql.read(fields=["device_id", "name"]).as_list()
        self.assertEqual(len(ret), 5)
        for row in ret:
            self.assertEqual(len(row), 2)
            self.assertTrue("device_id" in row)
            self.assertTrue("name" in row)
            self.assertFalse("desc" in row)

    def test_data_io_handler_read_with_where(self):
        ret = IoTDevice.sql.read(where=[
            "device_id = :device_id",
        ], device_id="2").as_list()
        self.assertEqual(len(ret), 1)
        for row in ret:
            self.assertEqual(row["device_id"], "2")

        ret = IoTDevice.sql.read(where=[
            "name = :name",
        ], name="name101").as_list()
        self.assertEqual(len(ret), 2)
        for row in ret:
            self.assertEqual(row["name"], "name101")

    def test_data_io_handler_read_with_limit(self):
        ret = IoTDevice.sql.read(limit=3).as_list()
        self.assertEqual(len(ret), 3)

    def test_data_io_handler_read_with_offset(self):
        ret = IoTDevice.sql.read(offset=3).as_list()
        self.assertEqual(len(ret), 2)


class TestIoTDevice_DataIOHander_DataFrame(unittest.TestCase):
    def setUp(self):
        create_all_tables()
        self.data = [
            {"device_id": "1", "name": "name01", "desc": "desc01"},
            {"device_id": "2", "name": "name02", "desc": "desc02"},
            {"device_id": "3", "name": "name03", "desc": "desc03"},
            {"device_id": "4", "name": "name101", "desc": "desc04"},
            {"device_id": "5", "name": "name101", "desc": "desc05"},
        ]
        self.df = pd.DataFrame(self.data)[["device_id", "name", "desc"]]
        IoTDevice.sql.write(self.df)

    def tearDown(self):
        drop_all_tables()

    def test_data_io_handler_read_all(self):
        df = IoTDevice.sql.read().as_df()
        self.assertEqual(len(df), 5)
        self.assertTrue("device_id" in df.columns)
        self.assertTrue("name" in df.columns)
        self.assertTrue("desc" in df.columns)

    def test_data_io_handler_read_with_fields(self):
        df = IoTDevice.sql.read(fields=["device_id", "name", "desc"]).as_df()
        self.assertTrue(df.equals(self.df))

        df = IoTDevice.sql.read(fields=["device_id", "name"]).as_df()
        self.assertEqual(len(df), 5)
        self.assertEqual(len(df.columns), 2)
        self.assertTrue("device_id" in df.columns)
        self.assertTrue("name" in df.columns)
        self.assertFalse("desc" in df.columns)

    def test_data_io_handler_read_with_where(self):
        df = IoTDevice.sql.read(where=[
            "device_id = :device_id",
        ], device_id="2").as_df()
        self.assertEqual(len(df), 1)
        self.assertEqual(len(df["device_id"].unique()), 1)
        self.assertEqual(df["device_id"][0], "2")

        df = IoTDevice.sql.read(where=[
            "name = :name",
        ], name="name101").as_df()
        self.assertEqual(len(df), 2)
        self.assertEqual(len(df["name"].unique()), 1)
        self.assertEqual(df["name"][0], "name101")
        self.assertEqual(df["name"][1], "name101")

    def test_data_io_handler_read_with_limit(self):
        df = IoTDevice.sql.read(limit=3).as_df()
        self.assertEqual(len(df), 3)

    def test_data_io_handler_read_with_offset(self):
        df = IoTDevice.sql.read(offset=3).as_df()
        self.assertEqual(len(df), 2)


class TestIoTDevice_DataIOHander_Stream(unittest.TestCase):
    def setUp(self):
        create_all_tables()
        self.data = [
            {"device_id": "1", "name": "name01", "desc": "desc01"},
            {"device_id": "2", "name": "name02", "desc": "desc02"},
            {"device_id": "3", "name": "name03", "desc": "desc03"},
            {"device_id": "4", "name": "name101", "desc": "desc04"},
            {"device_id": "5", "name": "name101", "desc": "desc05"},
        ]
        IoTDevice.sql.write(self.data)

    def tearDown(self):
        drop_all_tables()

    def test_data_io_handler_read_all(self):
        for stream in IoTDevice.sql.read().as_stream(batch_size=10):
            ret = stream.as_list()
            self.assertEqual(len(ret), 5)

        stream_result = IoTDevice.sql.read().as_stream(batch_size=1)
        for idx, stream in enumerate(stream_result, start=1):
            ret = stream.as_list()
            self.assertEqual(ret[0]["device_id"], f"{idx}")

        stream_result = IoTDevice.sql.read().as_stream(batch_size=1)
        for idx, stream in enumerate(stream_result, start=1):
            df = stream.as_df()
            self.assertEqual(df["device_id"][0], f"{idx}")


if __name__ == '__main__':
    unittest.main()
