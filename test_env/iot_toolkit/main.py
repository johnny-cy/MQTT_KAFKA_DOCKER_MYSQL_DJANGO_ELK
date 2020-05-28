#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

import epa.logging


logger = epa.logging.get_logger(__name__)


def main_func(coordinator, process_name="", description=""):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("config_files", help="config files", nargs='+')
    args = parser.parse_args()

    logger.info(f"Start {process_name}")

    threads = []
    for config in args.config_files:
        t = coordinator(config_file=config)
        t.start()
        threads.append(t)
        time.sleep(5)

    logger.info(f"{len(threads)} {coordinator.__name__} created.")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        for t in threads:
            t.terminated = True
            t.stop_event.set()

    logger.warning("Oop !!!")
