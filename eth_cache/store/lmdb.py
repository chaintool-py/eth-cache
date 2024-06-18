# standard imports
import os
import json
import logging

# external imports
import lmdb
from hexathon import strip_0x
from chainlib.eth.tx import (
        Tx,
        pack,
        )

# local imports
from . import StoreAction
from eth_cache.store.fs import FsStore

logg = logging.getLogger(__name__)


def to_path_key(path, k):
    if type(k) == str:
        k = k.encode('utf-8')
    elif type(k) == int:
        k = k.to_bytes(8, byteorder='big')
    if path[len(path)-1] != '/':
        path += '/'
    return path.encode('utf-8') + k


class LmdbStoreAdder:

    def __init__(self, action, db):
        self.action = action
        self.db = db


    def add(self, k, v):
        print("adding {} {} {}\n".format(self.action, k, v))
        dbk = to_path_key(self.action.value, k)
        with self.db.begin(write=True) as tx:
            tx.put(dbk, v)

    
class LmdbStore(FsStore):

    def __init__(self, chain_spec, cache_root=None, address_rules=None):
        super(LmdbStore, self).__init__(chain_spec, cache_root=cache_root, address_rules=address_rules)
        self.db = lmdb.open(self.cache_dir, create=True)
        for action in StoreAction:
            self.register_adder(action, LmdbStoreAdder(action, self.db))


    def put_tx(self, tx, include_data=False):
        super(LmdbStore, self).put_tx(tx, include_data=include_data)
#        raw = pack(tx.src, self.chain_spec)
#        tx_hash_dirnormal = strip_0x(tx.hash).upper()
#        tx_hash_bytes = bytes.fromhex(tx_hash_dirnormal)
#        k = self.__to_path_key('tx_raw', tx_hash_bytes)
#        with self.db.begin(write=True) as tx:
#            tx.put(k, raw)


    def get_tx(self, tx_hash):
        k = bytes.fromhex(tx_hash)
        k = to_path_key(StoreAction.TX.value, k)
        with self.db.begin() as tx:
            return tx.get(k)


    def get_rcpt(self, tx_hash):
        k = bytes.fromhex(tx_hash)
        k = to_path_key(StoreAction.RCPT.value, k)
        with self.db.begin() as tx:
            return tx.get(k)


    def get_block(self, block_hash):
        k = bytes.fromhex(block_hash)
        k = to_path_key(StoreAction.BLOCK.value, k)
        with self.db.begin() as tx:
            return tx.get(k)


    def get_block_number(self, block_number):
        r = None
        k = block_number.to_bytes(8, byteorder='big')
        k = to_path_key(StoreAction.BLOCK_NUM.value, k)
        with self.db.begin() as tx:
            r = tx.get(k)
        return self.get_block(r.hex())


    def put_address(self, tx, address):
        pass


    def __str__(self):
        return 'LmdbStore: root {}'.format(self.cache_dir)
