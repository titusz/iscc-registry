# -*- coding: utf-8 -*-
import os
from pathlib import Path
from loguru import logger as log
import iscc
from iscc_cli import lib, utils
from iscc_registry.contract.deploy import get_w3, compile_registry


DEMO_FILE = Path(__file__)
CONTRACT_ADDRESS = "0xbCb7976C14Ae16923aBEf972EC92044e3302a13E"


def get_live_contract(addr=CONTRACT_ADDRESS):
    return get_w3().eth.contract(address=addr, abi=compile_registry()["abi"])


def publish(file=DEMO_FILE):
    result = lib.iscc_from_file(file)
    log.debug(f"Created ISCC: {result}")
    iscc_code = result["iscc"]
    components = utils.iscc_split(iscc_code)
    iscc_raw = b"".join([iscc.decode(code)[1:] for code in components])
    log.debug(f"Raw ISCC ({len(iscc_raw)} bytes): {iscc_raw.hex()}")

    # Random CID for now (testing only)
    cid_raw = os.urandom(32)
    ct = get_live_contract()
    tx_hash_digest = ct.functions.register(iscc=iscc_raw, cid=cid_raw).transact()
    log.debug(f"ISCC registered (txid: {tx_hash_digest.hex()})")
    return tx_hash_digest.hex()


if __name__ == "__main__":
    publish()
