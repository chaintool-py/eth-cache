# external imports
from chainlib.eth.tx import (
        unpack,
        Tx,
        )
from hexathon import strip_0x


def apply(c, context, result, chain_spec, signed_tx, conn=None, block=None):
    signed_tx_bytes = bytes.fromhex(strip_0x(signed_tx))
    tx_src = unpack(signed_tx_bytes, chain_spec)
    tx = Tx(tx_src)
    if conn != None:
        raise NotImplementedError('retrieval of receipt from RPC connection not yet implemented')       
    if block != None:
        raise NotImplementedError('application of block for tx not yet implemented')
    return tx
