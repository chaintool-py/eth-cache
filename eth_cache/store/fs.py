# standard imports
import os
import json

# local imports
from eth_cache.store.base import Store
from eth_cache.store.base import StoreAction
from hexathon import strip_0x


default_base_dir = '/var/lib'

def chain_dir_for(chain_spec, base_dir=default_base_dir):
    chain_dir = os.path.join(base_dir, str(chain_spec).replace(':', '/'))
    return os.path.join(chain_dir, 'eth_cache')


class FsStore(Store):

    def put_block(self, block, include_data=False):
        hash_bytes = bytes.fromhex(strip_0x(block.hash))
        self.add(StoreAction.BLOCK_NUM, block.number, hash_bytes)
        num_bytes = block.number.to_bytes(8, 'big')
        self.add(StoreAction.BLOCK_HASH, hash_bytes, num_bytes)
        if include_data:
            src = json.dumps(block.src).encode('utf-8')
            self.add(StoreAction.BLOCK, hash_bytes, src)


    def __init__(self, chain_spec, cache_root=None, address_rules=None):
        if cache_root == None:
            cache_root = default_base_dir
        super(FsStore, self).__init__(chain_spec, cache_root=cache_root, address_rules=address_rules)
        self.chain_dir = chain_dir_for(chain_spec, cache_root)
        self.cache_dir = self.chain_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.block_src_path = os.path.join(self.cache_dir, StoreAction.BLOCK.value)
        self.block_num_path = os.path.join(self.cache_dir, StoreAction.BLOCK_NUM.value)
        self.block_hash_path = os.path.join(self.cache_dir, StoreAction.BLOCK_HASH.value)
        self.tx_path = os.path.join(self.cache_dir, StoreAction.TX.value)
        self.tx_raw_path = os.path.join(self.cache_dir, StoreAction.TX_RAW.value)
        self.rcpt_path = os.path.join(self.cache_dir, StoreAction.RCPT.value)
        self.rcpt_raw_path = os.path.join(self.cache_dir, StoreAction.RCPT_RAW.value)
        self.address_path = os.path.join(self.cache_dir, StoreAction.ADDRESS.value)
