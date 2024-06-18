# standard imports
import unittest
import json

# external imports
from chainlib.eth.address import is_same_address
from hexathon import strip_0x

# local imports
from eth_cache.store.lmdb import LmdbStore
from tests.util import TestCache


class TestCacheBasic(TestCache):

    def setUp(self):
        super(TestCacheBasic, self).setUp()
        self.store = LmdbStore(self.chain_spec, cache_root=self.cache_dir, address_rules=self.address_rules)


    def test_tx(self):
        self.store.put_tx(self.tx, include_data=True)
        j = self.store.get_tx(self.tx.hash)
        tx = json.loads(j)
        self.assertTrue(is_same_address(tx['hash'], self.tx.hash))


    def test_rcpt(self):
        self.store.put_tx(self.tx, include_data=True)
        j = self.store.get_rcpt(self.tx.hash)
        rcpt = json.loads(j)
        self.assertTrue(is_same_address(rcpt['transaction_hash'], self.tx.hash))


    def test_block_number(self):
        self.store.put_block(self.block, include_data=True)
        block_hash = strip_0x(self.block.hash)
        block_number = int(self.block.number)
        j = self.store.get_block_number(block_number)
        print("foo {}".format(j))
        block = json.loads(j)
        retrieved_block_hash = strip_0x(block['hash'])
        self.assertEqual(retrieved_block_hash, block_hash)


if __name__ == '__main__':
    unittest.main()
