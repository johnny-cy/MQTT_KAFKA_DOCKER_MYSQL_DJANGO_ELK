#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import epa.logging

from . import Handler


logger = epa.logging.get_logger(__name__)
es_hosts = ["elasticsearch:9200"]
#es_hosts = ["127.0.0.1:9200"]


class ESHandler(Handler):
    handler_id = "elasticsearch"

    def __init__(self, index, index_settings={}, ingest_settings={},
            id_fields=[], hosts=es_hosts):
        self.es = Elasticsearch(hosts)

        self._index = index
        self._id_fields = id_fields

        if index_settings:
            self.es.indices.create(index=self._index,
                    ignore=400, body=index_settings)
        if ingest_settings:
            self.es.ingest.put_pipeline(**ingest_settings)
            self._pipeline = ingest_settings["id"]
        else:
            self._pipeline = None

    def close(self):
        pass

    def write(self, data):
        if not isinstance(data, (list, tuple)):
            data = [data]

        def gendata():
            for x in data:
                x_id = "_".join(x[f] for f in self._id_fields)
                ret = {
                    "_op_type": "update",
                    "_index": self._index,
                    "_type": "_doc",
                    #"pipeline": self._pipeline, # not works for "update"
                    "_id": x_id,
                    "doc": x,
                    "doc_as_upsert": True,
                }
                yield ret

        bulk(self.es, gendata(), chunk_size=1000)

