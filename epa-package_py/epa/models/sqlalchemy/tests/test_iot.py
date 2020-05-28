#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from epa.models.sqlalchemy import sqlalchemy_db, session_scope
from epa.models.sqlalchemy.iot import IoTDevice


class TestIoTDevice(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        sqlalchemy_db.declarative_base.metadata.drop_all()

    def test_createing_iot_device_object(self):
        device_id = "KEOIDUV"
        with session_scope() as session:
            obj = IoTDevice(device_id=device_id)
            session.add(obj)

        with session_scope() as session:
            ret = session.query(IoTDevice).one()
            self.assertEqual(ret.device_id, device_id)


if __name__ == '__main__':
    unittest.main()
