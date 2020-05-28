#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from epa.models.iot import (IoTDevice, IoTRawData, IoTRawDataCount,
                            IoTEvent, IoTCircle)
from epa.models.lass import LassDevice, LassRawData, LassRawDataCount
from epa.models.epa_station import (EpaStationTextarDevice,
                                    EpaStationTextarRawData,
                                    EpaStationTextarRawDataCount,
                                    EpaStationTextarAbnormal,
                                    )
from epa.models.sensor_fusion import TaichungPM25

EpaStationRawData = EpaStationTextarRawData
EpaStationDevice = EpaStationTextarDevice

__all__ = [
    IoTDevice, IoTRawData, IoTRawDataCount, IoTEvent, IoTCircle,
    LassDevice, LassRawData,
    EpaStationDevice, EpaStationRawData,
    EpaStationTextarDevice, EpaStationTextarRawData,
    EpaStationTextarRawDataCount, EpaStationTextarAbnormal,
    TaichungPM25,
]
