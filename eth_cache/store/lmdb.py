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
        dbk = to_path_key(self.action.value, k)
        with self.db.begin(write=True) as dbtx:
            dbtx.put(dbk, v)

    
class LmdbStore(FsStore):

    def __init__(self, chain_spec, cache_root=None, address_rules=None):
        super(LmdbStore, self).__init__(chain_spec, cache_root=cache_root, address_rules=address_rules)
        self.db = lmdb.open(self.cache_dir, create=True)
        for action in StoreAction:
            self.register_adder(action, LmdbStoreAdder(action, self.db))


    def put_tx(self, tx, include_data=False):
        super(LmdbStore, self).put_tx(tx, include_data=include_data)


    def get_tx(self, tx_hash):
        k = bytes.fromhex(tx_hash)
        k = to_path_key(StoreAction.TX.value, k)
        with self.db.begin() as dbtx:
            return dbtx.get(k)


    def get_rcpt(self, tx_hash):
        k = bytes.fromhex(tx_hash)
        k = to_path_key(StoreAction.RCPT.value, k)
        with self.db.begin() as dbtx:
            return dbtx.get(k)


    def get_block(self, block_hash):
        k = bytes.fromhex(block_hash)
        k = to_path_key(StoreAction.BLOCK.value, k)
        with self.db.begin() as dbtx:
            return dbtx.get(k)


    def get_block_number(self, block_number):
        r = None
        k = block_number.to_bytes(8, byteorder='big')
        k = to_path_key(StoreAction.BLOCK_NUM.value, k)
        with self.db.begin() as dbtx:
            r = dbtx.get(k)
        return self.get_block(r.hex())


    def get_address_tx(self, address):
        k = bytes.fromhex(address)
        ok = to_path_key(StoreAction.ADDRESS.value, k)
        tx_hashes = []
        with self.db.begin() as dbtx:
            dbcr = dbtx.cursor()
            v = dbcr.set_range(ok)
            if v == None:
                return tx_hashes
            l = len(ok)
            for k, v in dbcr:
                if k[:l] != ok:
                    return tx_hashes
                tx_hashes.append(v)


    def put_address(self, tx, address):
        address_bytes = bytes.fromhex(strip_0x(address))
        tx_hash_bytes = bytes.fromhex(strip_0x(tx.hash))
        k = address_bytes + tx_hash_bytes + b'.start'

        with self.db.begin() as dbtx:
            r = dbtx.get(k)
            if r != None:
                return

        num = tx.block.number
        v = num.to_bytes(8, byteorder='big')
        self.add(StoreAction.ADDRESS, k, v)


    def __str__(self):
        return 'LmdbStore: root {}'.format(self.cache_dir)
