# -*- coding: utf-8 -*-
import base58
import iscc
import varint
from iscc_cli.utils import iscc_split


def cid_to_sha256(cid_v0):
    digest = base58.b58decode(cid_v0)
    sha256_digest = digest.lstrip(b"\x12\x20")
    return sha256_digest


def sha256_to_cid(sha256_digest):
    multi_hash = b"\x12" + b"\x20" + sha256_digest
    cid_v0 = base58.b58encode(multi_hash).decode("ascii")
    return cid_v0


def iscc_decode(code):
    return b"".join(iscc.decode(c) for c in iscc_split(code))


def build_iscc_id(ledger_id, iscc_code, counter):
    """Create ISCC-ID from full ISCC for given ledger with a given counter"""
    digest = iscc_decode(iscc_code)
    cid = digest[10:13]
    did = digest[20:22]
    iid = digest[29:31]
    return iscc.encode(ledger_id + cid + did + iid + varint.encode(counter))
