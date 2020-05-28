#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import yaml

from handler import get_handler_cls
from iot import IoTProject


class ConfigNotFoundError(Exception):
    """Yaml config file not found"""


class YamlConfig(object):

    def __init__(self, cls_name, config_file=None):
        if config_file is None:
            raise ConfigNotFoundError

        with open(config_file) as f:
            config = yaml.safe_load(f)

        self.project = IoTProject(config["code"],
                                  config["project"],
                                  config["api_key"])

        cls_config = config[cls_name]
        handlers = config["handlers"]

        self.input = self.gen_handler(handlers[cls_config["input"]],
                name=cls_config["input"])
        self.output = self.gen_handler(handlers[cls_config["output"]],
                name=cls_config["output"])

        if "args" in cls_config:
            for k, v in cls_config["args"].items():
                setattr(self, k, v)

    def gen_handler(self, handler_config, name=None):
        handler_cls = get_handler_cls(handler_config["handler"])
        args = handler_config["args"] if "args" in handler_config else {}
        ret = handler_cls(**args)
        ret.name = name
        ret.project = self.project
        return ret

