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
from eth_cache.store.fs import FsStore

logg = logging.getLogger(__name__)



class LmdbStore(FsStore):

    def __init__(self, chain_spec, cache_root=None, address_rules=None):
        super(LmdbStore, self).__init__(chain_spec, cache_root=cache_root, address_rules=address_rules)
        self.db = lmdb.open(self.cache_dir, create=True)


    def __to_path_key(self, path, k):
        if path[len(path)-1] != '/':
            path += '/'
        return path.encode('utf-8') + k


    def put_tx(self, tx, include_data=False):
        raw = pack(tx.src, self.chain_spec)
        tx_hash_dirnormal = strip_0x(tx.hash).upper()
        tx_hash_bytes = bytes.fromhex(tx_hash_dirnormal)
        k = self.__to_path_key('tx_raw', tx_hash_bytes)
        with self.db.begin(write=True) as tx:
            tx.put(k, raw)


    def get_tx(self, tx_hash):
        self.__to_path_key(self, path, key)


    def __str__(self):
        return 'RockDbStore: root {}'.format(self.cache_dir)
