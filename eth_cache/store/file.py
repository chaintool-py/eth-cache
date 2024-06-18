# standard imports
import os
import json
import logging

# external imports
from hexathon import strip_0x
from chainlib.eth.tx import (
        Tx,
        )
from leveldir.numeric import NumDir
from leveldir.hex import HexDir

# local imports
from eth_cache.store.fs import FsStore
from eth_cache.store.base import StoreAction

logg = logging.getLogger(__name__)


class FileStore(FsStore):


    def add_address_dir(self, dirhsh, address):
        address_dir_adder = self.adder[StoreAction.ADDRESS]
        address_dir_adder.add_dir(dirhsh, address, b'')


    def put_address(self, tx, address):
        a_hex = strip_0x(address).upper()
        a = bytes.fromhex(a_hex)
        #self.address_dir.add_dir(tx_hash_dirnormal, a, b'')
        #address_dir_adder = self.adder[StoreAction.ADDRESS]
        #address_dir_adder.add_dir(tx_hash_dirnormal, a, b'')
        #self.add_address_dir(tx_hash_dirnormal, a)
        tx_hash = strip_0x(tx.hash).upper()
        self.add_address_dir(tx_hash, a)
        #dirpath = self.address_dir.to_filepath(a_hex)
        #dirpath = address_dir_adder.to_filepath(a_hex)
        dirpath = self.to_filepath(StoreAction.ADDRESS, a_hex)
        fp = os.path.join(dirpath, '.start')
        num = tx.block.number
        num_compare = 0
        try:
            f = open(fp, 'rb')
            r = f.read(8)
            f.close()
            num_compare = int.from_bytes(r, 'big')
        except FileNotFoundError:
            pass

        if num_compare == 0 or num < num_compare:
            logg.debug('recoding new start block {} for {}'.format(num, a))
            num_bytes = num.to_bytes(8, 'big')
            f = open(fp, 'wb')
            f.write(num_bytes)
            f.close()


    def put_tx(self, tx, include_data=False):
        super(FileStore, self).put_tx(tx, include_data=include_data) 
        

    def get_block_number(self, block_number):
        #fp = self.block_num_dir.to_filepath(block_number)
        fp = self.to_filepath(StoreAction.BLOCK_NUM, block_number)
        f = open(fp, 'rb')
        r = f.read()
        f.close()
        return self.get_block(r.hex())


    def get_block(self, block_hash):
        #fp = self.block_src_dir.to_filepath(block_hash)
        fp = self.to_filepath(StoreAction.BLOCK, block_hash)
        f = open(fp, 'rb')
        r = f.read()
        f.close()
        return r


    def get_tx(self, tx_hash):
        #fp = self.tx_dir.to_filepath(tx_hash)
        fp = self.to_filepath(StoreAction.TX, tx_hash)
        f = open(fp, 'rb')
        r = f.read()
        f.close()
        return r


    def get_rcpt(self, tx_hash):
        #fp = self.rcpt_dir.to_filepath(tx_hash)
        fp = self.to_filepath(StoreAction.RCPT, tx_hash)
        f = open(fp, 'rb')
        r = f.read()
        f.close()
        return r


    def get_address_tx(self, address):
        #fp = self.address_dir.to_filepath(address)
        fp = self.to_filepath(StoreAction.ADDRESS, address)
        tx_hashes = []
        for tx_hash in os.listdir(fp):
            if tx_hash[0] == '.':
                continue
            tx_hashes.append(tx_hash)
        return tx_hashes


    def __init__(self, chain_spec, cache_root=None, address_rules=None):
        super(FileStore, self).__init__(chain_spec, cache_root=cache_root, address_rules=address_rules)
        block_src_dir = HexDir(self.block_src_path, 32, levels=2)
        self.register_adder(StoreAction.BLOCK, block_src_dir)
        block_num_dir = NumDir(self.block_num_path, [100000, 1000])
        self.register_adder(StoreAction.BLOCK_NUM, block_num_dir)
        block_hash_dir = HexDir(self.block_hash_path, 32, levels=2)
        self.register_adder(StoreAction.BLOCK_HASH, block_hash_dir)
        tx_dir = HexDir(self.tx_path, 32, levels=2)
        self.register_adder(StoreAction.TX, tx_dir)
        tx_raw_dir = HexDir(self.tx_raw_path, 32, levels=2)
        self.register_adder(StoreAction.TX_RAW, tx_raw_dir)
        rcpt_dir = HexDir(self.rcpt_path, 32, levels=2)
        self.register_adder(StoreAction.RCPT, rcpt_dir)
        rcpt_raw_dir = HexDir(self.rcpt_raw_path, 32, levels=2)
        self.register_adder(StoreAction.RCPT_RAW, rcpt_raw_dir)
        address_dir = HexDir(self.address_path, 20, levels=2)
        self.register_adder(StoreAction.ADDRESS, address_dir)


    def __str__(self):
        return 'FileStore: root {}'.format(self.cache_dir)
