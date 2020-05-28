#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

import connexion
from connexion.apps.flask_app import FlaskJSONEncoder


class CameoFlaskJSONEncoder(FlaskJSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs["indent"] = None
        kwargs["ensure_ascii"] = False
        kwargs["separators"] = (",", ":")
        super().__init__(*args, **kwargs)

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat(" ")

        return super().default(o)


app = connexion.FlaskApp(__name__, specification_dir="./")
app.app.json_encoder = CameoFlaskJSONEncoder

# TODO: FIXME: workaround
#   Both share the same name "/_/api/v2". Blueprints that are created on the fly need unique names.
# app.add_api("api/epa_station/swagger.yml", base_path='/_/api/v2')
# app.add_api("api/iot/swagger.yml", base_path='/_/api/v2')
app.add_api("api/swagger.yml", base_path='/_/api/v2')


application = app.app   # expose global WSGI application object


if __name__ == "__main__":
    app.run(port=8002)
