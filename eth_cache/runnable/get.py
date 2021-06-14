# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import sys
import os
import argparse
import logging
import select

# external imports
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import (
        pack,
        receipt,
        transaction,
        Tx,
        )
from chainlib.eth.block import (
        Block,
        block_by_hash,
        )
from hexathon import strip_0x

# local imports
from eth_cache.store import (
        PointerHexDir,
        TxFileStore,
        )

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')
default_data_dir = os.path.realpath(os.path.join(os.environ.get('HOME', ''), '.eth_cache'))

def stdin_arg(t=0):
    h = select.select([sys.stdin], [], [], t)
    if len(h[0]) > 0:
        v = h[0][0].read()
        return v.rstrip()
    return None


argparser = argparse.ArgumentParser('eth-get', description='display information about an Ethereum address or transaction', epilog='address/transaction can be provided as an argument or from standard input')
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('--data-dir', dest='data_dir', type=str, help='Be more verbose')
argparser.add_argument('tx_hash', nargs='?', default=stdin_arg(), type=str, help='Item to get information for (address og transaction)')
args = argparser.parse_args()


if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

tx_hash = args.tx_hash
if tx_hash == None:
    tx_hash = stdin_arg(t=None)
    if tx_hash == None:
        argparser.error('need first positional argument or value from stdin')

chain_spec = ChainSpec.from_chain_str(args.i)
data_dir = args.data_dir
if data_dir == None:
    data_dir = os.path.join(default_data_dir, str(chain_spec))
rpc_provider = args.p

if __name__ == '__main__':
    rpc = EthHTTPConnection(rpc_provider)
    o = transaction(tx_hash)
    r = rpc.do(o)
    tx = Tx(r)
    tx_raw = pack(tx.src, chain_spec)

    o = receipt(tx_hash)
    r = rpc.do(o)
    tx.apply_receipt(r)

    rcpt = Tx.src_normalize(r)
    o = block_by_hash(rcpt['block_hash'])
    r = rpc.do(o)
    block = Block(r)
    tx.apply_block(block)

    store_backend = PointerHexDir(data_dir, 32)
    store_backend.register_pointer('address')
    store = TxFileStore(chain_spec, store_backend)
    #store_backend.add(bytes.fromhex(strip_0x(tx_hash)), tx_raw)
    store.put(block, tx, [])
