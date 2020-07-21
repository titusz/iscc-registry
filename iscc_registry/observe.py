# -*- coding: utf-8 -*-
"""Watching for registration events"""
import time
from dataclasses import dataclass

import base58
from loguru import logger as log
import iscc
from iscc_registry.publish import get_live_contract


@dataclass
class RegEntry:
    iscc: str
    actor: str
    cid: str
    tx_hash: str
    block_hash: str


def parse_event(evt):

    # encode ISCC
    iscc_codes = []
    for code_type in ("mc", "cc", "dc", "ic"):
        iscc_codes.append(iscc.encode(getattr(evt.args, code_type)))

    # encode CIDv0
    multi_hash = b"\x12" + b"\x20" + evt.args.cid
    cid = base58.b58encode(multi_hash).decode("ascii")

    return RegEntry(
        iscc="-".join(iscc_codes),
        actor=evt.address,
        cid=cid,
        tx_hash=evt.transactionHash.hex(),
        block_hash=evt.blockHash.hex(),
    )


def observe(from_block=0):
    co = get_live_contract()
    event_filter = co.events.Registration.createFilter(fromBlock=from_block)
    log.info("emit historic registration events")
    for event in event_filter.get_all_entries():
        log.info(parse_event(event))
    log.info("start watching new registration events")
    while True:
        for event in event_filter.get_new_entries():
            log.info(parse_event(event))
        time.sleep(2)


if __name__ == "__main__":
    observe()
