# -*- coding: utf-8 -*-
"""Domain based self verification"""
import json
import requests
from eth_account.messages import encode_defunct
from iscc_registry.conn import w3_client
from loguru import logger as log


def create_proof(domain: str, address: str) -> str:
    w3 = w3_client()
    sig = w3.eth.sign(address, text=domain)
    proof = {
        "address": address,
        "domain": domain,
        "signature": sig.hex(),
    }
    log.info(f"Signing {domain} with address {address}")
    return json.dumps(proof, indent=2)


def valid(domain: str, address: str, proof: dict) -> bool:
    w3 = w3_client()

    if address != proof["address"]:
        return False
    if domain != proof["domain"]:
        return False
    if not proof.get('signature'):
        return False

    msg = encode_defunct(text=proof["domain"])
    try:
        raddr = w3.eth.account.recover_message(msg, signature=proof["signature"])
    except Exception:
        return False

    if address != raddr:
        return False
    return True


def verify_proof(domain: str, address: str):
    url = domain + "/iscc-proof.json"
    try:
        log.info(f"Fetching self verification proof from {url}")
        result = requests.get(url)
        proof = result.json()
    except Exception as e:
        log.warning(f"Failed to fetch proof: {repr(e)}")
        return False
    log.info(f"Verifying domain proof {domain} for {address}")
    return valid(domain, address, proof)
