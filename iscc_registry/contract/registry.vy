"""
@title ISCC registration contract v0.0.1
@license MIT
@notice You can use this contract to register a unique ISCC-ID for you content.
"""

owner: address

event Registration:
    mc: Bytes[9]
    cc: Bytes[9]
    dc: Bytes[9]
    ic: Bytes[9]
    cid: bytes32

@external
def __init__():
    self.owner = msg.sender

@view
@external
def register(iscc: Bytes[36], cid: bytes32):
    """
    @notice Registrations are emitted as events and indexed by ISCC meta-registries.
    @param iscc Raw byte-digest of your ISCC
    @param cid  Raw sha256-digest of a CIDv0 that points to IPFS hosted data
    """
    # assert slice(iscc, 0, 1) == 0x00, "ISCC must start with 0x00 byte"
    mc: Bytes[9] = slice(iscc, 0, 9)
    cc: Bytes[9] = slice(iscc, 9, 9)
    dc: Bytes[9] = slice(iscc, 18, 9)
    ic: Bytes[9] = slice(iscc, 27, 9)
    log Registration(mc, cc, dc, ic, cid)

@external
@payable
def __default__():
    """
    @notice Collects ether sent to this contract
    """
    pass
