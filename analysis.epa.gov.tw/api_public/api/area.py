#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from epa.area import all_areas

def get(area=None,
        min_lat=-90.0, min_lon=-180.0,
        max_lat=90.0, max_lon=180,
        limit=10000,
        ):

    def _check(a):
        if area and area != a.name:
            return False
        if a.min_lat < min_lat or a.max_lat > max_lat or \
           a.min_lon < min_lon or a.max_lat > max_lon:
            return False
        else:
            return True

    def _to_dict(a):
        return {"name": a.name, "area_id": a.area_id,
                "min_lat": a.min_lat, "max_lat": a.max_lat,
                "min_lon": a.min_lon, "max_lon": a.max_lon,}

    data = [_to_dict(a) for a in all_areas if _check(a)]

    ret = {
        "count": len(data),
        "data": data,
        "errors": [],
    }
    return ret

