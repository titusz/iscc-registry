# -*- coding: utf-8 -*-
from pathlib import Path
from loguru import logger as log
import vyper
from iscc_registry.conn import w3_client


HERE = Path(__file__)
SOURCE_FILE = HERE.parent / "registry.vy"


def compile_registry() -> dict:
    """Compile registry contract."""
    with open(SOURCE_FILE, "rt") as infile:
        compiled = vyper.compile_code(infile.read(), ["abi", "bytecode"])
        log.debug(f"Compiled {SOURCE_FILE}")
        return compiled


def get_contract():
    """Build registry contract object."""
    return w3_client().eth.contract(**compile_registry())


def deploy(account=0):
    w3 = w3_client()
    w3.eth.defaultAccount = w3.eth.accounts[account]
    contract_obj = get_contract()
    tx_hash = contract_obj.constructor().transact()
    address = w3.eth.getTransactionReceipt(tx_hash)["contractAddress"]
    log.debug(f"Contract deployed to {address}")
    return address


if __name__ == "__main__":
    addr = deploy()
    log.info(f"Registry contract deployed to {addr}")
    log.info(f"Remember to set CONTRACT_ADDRESS env variable to {addr}")
