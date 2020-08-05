# -*- coding: utf-8 -*-
"""Watching for registration events"""
import time
from dataclasses import dataclass, asdict
import iscc_registry
from loguru import logger as log
import iscc
from iscc_registry.conn import db_client
from iscc_registry.publish import get_live_contract
from iscc_registry import tools
from iscc_registry.tools import build_iscc_id


@dataclass
class RegEntry:
    iscc: str
    actor: str
    cid: str = ""
    tx_hash: str = ""
    block_hash: str = ""
    block_num: int = 0


def parse_event(evt):

    # encode ISCC
    iscc_codes = []
    for code_type in ("mc", "cc", "dc", "ic"):
        iscc_codes.append(iscc.encode(getattr(evt.args, code_type)))

    # encode CIDv0
    cid = tools.sha256_to_cid(evt.args.cid)

    return RegEntry(
        iscc="-".join(iscc_codes),
        actor=evt.args.actor,
        cid=cid,
        tx_hash=evt.transactionHash.hex(),
        block_hash=evt.blockHash.hex(),
        block_num=evt.blockNumber,
    )


def observe(from_block=None, rebuild=False):
    """Watch ISCC-Registry contract events and index new registartion events."""
    meta_index = db_client()

    if rebuild:
        meta_index.clear()
        from_block = 0

    if from_block is None:
        if "height_eth" not in meta_index:
            meta_index["height_eth"] = 0
        from_block = meta_index["height_eth"]
    log.info(f"start observing from block {from_block}")
    co = get_live_contract()
    event_filter = co.events.Registration.createFilter(fromBlock=from_block)
    reg_entry = None
    log.info("observe historic registration events")
    for event in event_filter.get_all_entries():
        reg_entry = parse_event(event)
        log.info(f"observing historic {reg_entry}")
        index(reg_entry)
    if reg_entry:
        meta_index["height_eth"] = reg_entry.block_num
    log.info("start watching new registration events")
    while True:
        for event in event_filter.get_new_entries():
            reg_entry = parse_event(event)
            log.info(f"observing {reg_entry}")
            index(reg_entry)
        if reg_entry:
            meta_index["height_eth"] = reg_entry.block_num
        time.sleep(2)


def index(reg_entry: RegEntry) -> str:
    meta_index = db_client()
    counter = 0
    iscc_id = build_iscc_id(iscc_registry.LEDGER_ID_ETH, reg_entry.iscc, counter)
    while iscc_id in meta_index:
        if meta_index[iscc_id]["actor"] == reg_entry.actor:
            log.info(f"updateing {iscc_id} -> {reg_entry}")
            meta_index[iscc_id] = asdict(reg_entry)
            break
        counter += 1
        log.info(f"counting up {iscc_id}")
        iscc_id = build_iscc_id(iscc_registry.LEDGER_ID_ETH, reg_entry.iscc, counter)
    meta_index[iscc_id] = asdict(reg_entry)
    log.info(f"indexed {iscc_id} -> {reg_entry}")
    return iscc_id


def find_next(reg_entry: RegEntry) -> str:
    meta_index = db_client()
    counter = 0
    iscc_id = build_iscc_id(iscc_registry.LEDGER_ID_ETH, reg_entry.iscc, counter)
    while iscc_id in meta_index:
        if meta_index[iscc_id]["actor"] == reg_entry.actor:
            log.info(
                f"Previously registered by same actor. This will be an update: {iscc_id} -> {reg_entry}"
            )
            return iscc_id
        counter += 1
        log.info(f"counting up {iscc_id}")
        iscc_id = build_iscc_id(iscc_registry.LEDGER_ID_ETH, reg_entry.iscc, counter)
    return iscc_id


if __name__ == "__main__":
    observe()
