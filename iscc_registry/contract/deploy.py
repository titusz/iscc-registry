# -*- coding: utf-8 -*-
from loguru import logger as log
from web3 import Web3
import vyper

SOURCE_FILE = 'registry.vy'
WEB3_URL = 'http://127.0.0.1:7545'


def deploy():
    with open(SOURCE_FILE, 'rt') as infile:
        compiled = vyper.compile_code(infile.read(), ['abi', 'bytecode'])
        log.debug(f'Compiled {SOURCE_FILE}')
    w3 = Web3(Web3.HTTPProvider(WEB3_URL))
    log.debug(f'Connected: {w3.isConnected()}')
    w3.eth.defaultAccount = w3.eth.accounts[0]
    contract_obj = w3.eth.contract(**compiled)
    tx_hash = contract_obj.constructor().transact()
    address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
    log.debug(f"Contract deployed to {address}")
    return address


if __name__ == '__main__':
    deploy()
