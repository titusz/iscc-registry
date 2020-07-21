# -*- coding: utf-8 -*-
"""Watching for registration events"""
import time
from loguru import logger as log
from iscc_registry.publish import get_live_contract


def observe(from_block=0):
    co = get_live_contract()
    event_filter = co.events.Registration.createFilter(fromBlock=from_block)
    log.info('emit historic registration events')
    for event in event_filter.get_all_entries():
        log.info(event)
    log.info('start watching new registration events')
    while True:
        for event in event_filter.get_new_entries():
            log.info(event)
        time.sleep(2)


if __name__ == '__main__':
    observe()
