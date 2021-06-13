# standard imports
import tempfile
import os
import logging
import sys

# external imports
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.block import (
        block_by_number,
        block_by_hash,
        block_latest,
        Block,
        )
from chainlib.eth.tx import (
        Tx,
        transaction,
        receipt,
        )
from chainlib.interface import ChainInterface
from chainsyncer.backend.memory import MemBackend
from chainsyncer.driver.threadpool import ThreadPoolHistorySyncer

# local imports
from eth_cache.account import AccountRegistry
from eth_cache.store import TxFileStore
from eth_cache.store import PointerHexDir

logging.basicConfig(level=logging.INFO)
logg = logging.getLogger()
logging.getLogger('eth_cache.store').setLevel(logging.DEBUG)
logging.getLogger('chainsyncer.driver.threadpool').setLevel(logging.DEBUG)
logging.getLogger('chainsyncer.driver.head').setLevel(logging.DEBUG)
#logging.getLogger('chainsyncer.backend.memory').setLevel(logging.DEBUG)

root_dir = tempfile.mkdtemp(dir=os.path.join('/tmp/ethsync'))
data_dir = os.path.join(root_dir, 'store')
logg.info('using data dir {}'.format(data_dir))

chain_interface = ChainInterface()
chain_interface.set('block_by_number', block_by_number)
chain_interface.set('block_by_hash', block_by_hash)
chain_interface.set('block_latest', block_latest)
chain_interface.set('block_from_src', Block.from_src)
chain_interface.set('tx_from_src', Tx.from_src)
chain_interface.set('tx_by_hash', transaction)
chain_interface.set('tx_receipt', receipt)
chain_interface.set('src_normalize', Tx.src_normalize)

chain_spec = ChainSpec('evm', 'ethereum', 1)
backend = PointerHexDir(data_dir, 32)
backend.register_pointer('address')
store = TxFileStore(chain_spec, backend)

def conn_factory():
    return EthHTTPConnection('http://localhost:8545')
    #return EthHTTPConnection('http://localhost:63545')
rpc = conn_factory()

#start = 8534365
start = 12423900
#start = 0

o = block_latest()
r = rpc.do(o)
stop = int(r, 16)
stop = start + 3

syncer_backend = MemBackend(chain_spec, None, target_block=stop)
syncer_backend.set(start, 0)

#o = block_by_number(12423955, include_tx=False)
#r = rpc.do(o)
##o = block_by_hash(r)
##r = rpc.do(o)
#block = Block(r)
#
#tx_hash = block.txs[308]
#logg.debug('tx_ahsh {}'.format(tx_hash))
#o = transaction(tx_hash)
#tx_src = rpc.do(o)
#o = receipt(tx_hash)
#rcpt = rpc.do(o)
#tx = Tx(tx_src, block=block)

account_registry = AccountRegistry()
account_registry.add('0x6bd8cb96bbc58a73d5360301b7791457bc93da24', 'money')

class StoreFilter:

    def __init__(self, store, registry):
        self.registry = registry
        self.store = store


    def filter(self, conn, block, tx, session=None):
        addresses = []
        if account_registry.have(tx.inputs[0]):
            addresses.append(tx.inputs[0])
        if account_registry.have(tx.outputs[0]):
            addresses.append(tx.outputs[0])
        store.put(block, tx, addresses)


class MonitorFilter:

    def __init__(self, name='sync'):
        self.name = name


    def filter(self, rpc, block, tx, session=None):
        if tx == None:
            s = '{} sync block error in tx lookup ({})'.format(self.name, block.number, len(block.txs))
        else:
            s = '{} sync block {} tx {}/{}'.format(self.name, block.number, tx.index, len(block.txs))
        sys.stdout.write('{:<100s}\r'.format(s))


fltr = StoreFilter(store, account_registry)

if __name__ == '__main__':
    ThreadPoolHistorySyncer.yield_delay = 0
    syncer = ThreadPoolHistorySyncer(conn_factory, 2, syncer_backend, chain_interface)
    syncer.add_filter(MonitorFilter())
    syncer.add_filter(fltr)
    syncer.loop(0, rpc)
