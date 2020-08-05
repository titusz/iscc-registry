# -*- coding: utf-8 -*-
from loguru import logger as log
import iscc
import iscc_registry
from iscc_cli.utils import iscc_split
from iscc_registry.deploy import w3_client, compile_registry
from iscc_registry import tools


def get_live_contract(addr=iscc_registry.settings.contract_address, account=0):
    w3 = w3_client()
    w3.eth.defaultAccount = w3.eth.accounts[account]
    return w3.eth.contract(address=addr, abi=compile_registry()["abi"])


def publish(iscc_code, cid, account=0):
    components = iscc_split(iscc_code)
    iscc_raw = b"".join([iscc.decode(code) for code in components])
    log.debug(f"Raw ISCC ({len(iscc_raw)} bytes): {iscc_raw.hex()}")
    cid_raw = tools.cid_to_sha256(cid)
    log.debug(f"Raw CIDv0 ({len(cid_raw)} bytes): {cid_raw.hex()}")
    ct = get_live_contract(account=account)
    tx_hash_digest = ct.functions.register(iscc=iscc_raw, cid=cid_raw).transact()
    log.debug(f"ISCC registered (txid: {tx_hash_digest.hex()})")
    return tx_hash_digest.hex()
