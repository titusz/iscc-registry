# -*- coding: utf-8 -*-
from loguru import logger as log
import ipfshttpclient
from web3 import Web3
import iscc_registry
from diskcache import Index


IPFS_CLIENT = None
W3_CLIENT = None
DB_CIENT = None
CHAINS = {
    1: "Ethereum mainnet",
    2: "Morden (disused), Expanse mainnet",
    3: "Ropsten",
    4: "Rinkeby",
    5: "Goerli",
    42: "Kovan",
    1337: "Geth private chains (default)",
}


def w3_client():
    """Return cached web3 connection."""
    global W3_CLIENT
    if not W3_CLIENT:
        W3_CLIENT = Web3(Web3.HTTPProvider(iscc_registry.settings.web3_address))
        if W3_CLIENT.isConnected():
            log.debug(
                f"Connected to {chain_name(W3_CLIENT)} via {iscc_registry.settings.web3_address}"
            )
        else:
            log.error("Connection failed")
    return W3_CLIENT


def ipfs_client():
    """Return cached ipfs connection."""
    global IPFS_CLIENT
    if IPFS_CLIENT is None:
        IPFS_CLIENT = ipfshttpclient.connect(iscc_registry.settings.ipfs_address)
    return IPFS_CLIENT


def db_client():
    """Return cached db connection"""
    global DB_CIENT
    if DB_CIENT is None:
        DB_CIENT = Index(iscc_registry.settings.db_dir)
    return DB_CIENT


def chain_name(w3_client):
    """Return chain name"""
    return CHAINS[w3_client.eth.chainId]
