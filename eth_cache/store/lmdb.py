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


logg = logging.getLogger(__name__)

default_base_dir = '/var/lib'


def chain_dir_for(chain_spec, base_dir=default_base_dir):
    chain_dir = os.path.join(base_dir, str(chain_spec).replace(':', '/'))
    return os.path.join(chain_dir, 'eth_cache')


class LmdbStore:

    def __init__(self, chain_spec, cache_root=default_base_dir, address_rules=None):
        # TODO: perhaps common for all
        self.chain_spec = chain_spec
        self.address_rules = address_rules
        # TODO: perhaps common for all fs
        self.chain_dir = chain_dir_for(chain_spec, cache_root)
        self.cache_dir = self.chain_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.block_src_path = os.path.join(self.cache_dir, 'block', 'src')
        self.block_num_path = os.path.join(self.cache_dir, 'block', 'num')
        self.block_hash_path = os.path.join(self.cache_dir, 'block', 'hash')
        self.tx_path = os.path.join(self.cache_dir, 'tx', 'src')
        self.tx_raw_path = os.path.join(self.cache_dir, 'tx', 'raw')
        self.rcpt_path = os.path.join(self.cache_dir, 'rcpt', 'src')
        self.rcpt_raw_path = os.path.join(self.cache_dir, 'rcpt', 'raw')
        self.address_path = os.path.join(self.cache_dir, 'address')
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
