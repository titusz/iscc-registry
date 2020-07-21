"""
@title ISCC registration contract v0.0.1
@license MIT
@notice You can use this contract to register a unique ISCC-ID for you content.
"""

event Registration:
    iscc: bytes32
    cid: bytes32


@external
def register(iscc: bytes32, cid: bytes32):
    """
    @notice Registrations are emitted as events and indexed by ISCC meta-registries.
    @param iscc Raw byte-digest of your ISCC
    @param cid  Raw sha256-digest of a CIDv0 that points to IPFS hosted data
    """
    log Registration(iscc, cid)
