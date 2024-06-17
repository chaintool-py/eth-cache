# standard imports
import unittest
import json

# external imports
from chainlib.eth.address import is_same_address

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


if __name__ == '__main__':
    unittest.main()
