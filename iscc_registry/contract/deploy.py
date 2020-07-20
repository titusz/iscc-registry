# -*- coding: utf-8 -*-
from pathlib import Path

from loguru import logger as log
from web3 import Web3
import vyper

HERE = Path(__file__)

SOURCE_FILE = HERE.parent / "registry.vy"
WEB3_URL = "http://127.0.0.1:7545"
_w3 = None


def get_w3():
    """Return cached web3 connection."""
    global _w3
    if not _w3:
        _w3 = Web3(Web3.HTTPProvider(WEB3_URL))
        _w3.eth.defaultAccount = _w3.eth.accounts[0]
        if _w3.isConnected():
            log.debug(f"Connected to {WEB3_URL}")
        else:
            log.error("Connection failed")
    return _w3


def compile_registry() -> dict:
    """Compile registry contract."""
    with open(SOURCE_FILE, "rt") as infile:
        compiled = vyper.compile_code(infile.read(), ["abi", "bytecode"])
        log.debug(f"Compiled {SOURCE_FILE}")
        return compiled


def get_contract():
    """Build registry contract object."""
    return get_w3().eth.contract(**compile_registry())


def deploy():
    w3 = get_w3()
    w3.eth.defaultAccount = w3.eth.accounts[0]
    contract_obj = get_contract()
    tx_hash = contract_obj.constructor().transact()
    address = w3.eth.getTransactionReceipt(tx_hash)["contractAddress"]
    log.debug(f"Contract deployed to {address}")
    return address


if __name__ == "__main__":
    deploy()
