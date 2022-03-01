# standard imports
import tempfile
import shutil
import unittest
import logging
import json

# external imports
from chainlib.chain import ChainSpec
from chainlib.eth.gas import (
        Gas,
        OverrideGasOracle,
        )
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.tx import (
        transaction,
        receipt,
        TxFormat,
        Tx,
        )
from chainlib.eth.block import (
        block_by_hash,
        Block,
        )
from chainlib.eth.address import is_same_address
from hexathon import strip_0x

# local imports
from eth_cache.store.file import FileStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestCache(EthTesterCase):

    def setUp(self):
        super(TestCache, self).setUp()
        fp = tempfile.mkdtemp()
        self.cache_dir = fp

        class Applier:
            def apply_rules_addresses(self, sender, recipient, address):
                return True

        self.store = FileStore(self.chain_spec, cache_root=self.cache_dir, address_rules=Applier())
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        gas_oracle = OverrideGasOracle(price=100000000000, limit=30000)
        c = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.create(self.accounts[0], self.accounts[1], 1024)
        r = self.rpc.do(o)

        o = transaction(tx_hash)
        tx_src = self.rpc.do(o)

        o = receipt(tx_hash)
        rcpt_src = self.rpc.do(o)

        o = block_by_hash(tx_src['block_hash'])
        block_src = self.rpc.do(o)

        self.block = Block(block_src)
        self.tx = Tx(tx_src, block=self.block, rcpt=rcpt_src)


    def tearDown(self):
        shutil.rmtree(self.cache_dir) 


    def test_tx(self):
        self.store.put_tx(self.tx, include_data=True)
        j = self.store.get_tx(self.tx.hash)
        tx = json.loads(j)
        self.assertTrue(is_same_address(tx['hash'], self.tx.hash))


    def test_block(self):
        self.store.put_block(self.block, include_data=True)
        block_hash = strip_0x(self.block.hash)
        j = self.store.get_block(block_hash)
        block = json.loads(j)
        retrieved_block_hash = strip_0x(block['hash'])
        self.assertEqual(retrieved_block_hash, block_hash)


    def test_block_number(self):
        self.store.put_block(self.block, include_data=True)
        block_hash = strip_0x(self.block.hash)
        block_number = int(self.block.number)
        j = self.store.get_block_number(block_number)
        block = json.loads(j)
        retrieved_block_hash = strip_0x(block['hash'])
        self.assertEqual(retrieved_block_hash, block_hash)


    def test_rcpt(self):
        self.store.put_tx(self.tx, include_data=True)
        j = self.store.get_rcpt(self.tx.hash)
        rcpt = json.loads(j)
        self.assertTrue(is_same_address(rcpt['transaction_hash'], self.tx.hash))


    def test_address(self):
        nonce_oracle = RPCNonceOracle(self.accounts[2], self.rpc)
        gas_oracle = OverrideGasOracle(price=100000000000, limit=30000)
        c = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.create(self.accounts[2], self.accounts[1], 1024)
        r = self.rpc.do(o)
        o = transaction(tx_hash)
        tx_src = self.rpc.do(o)

        o = block_by_hash(tx_src['block_hash'])
        block_src = self.rpc.do(o)
        block = Block(block_src)

        tx = Tx(tx_src, block=block)
        self.store.put_tx(tx, include_data=True)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.create(self.accounts[1], self.accounts[0], 1024)
        r = self.rpc.do(o)
        o = transaction(tx_hash)
        tx_src = self.rpc.do(o)

        o = block_by_hash(tx_src['block_hash'])
        block_src = self.rpc.do(o)
        block = Block(block_src)

        tx = Tx(tx_src, block=block)
        self.store.put_tx(tx, include_data=True)

        address = strip_0x(self.accounts[1])
        txs = self.store.get_address_tx(address)
        self.assertEqual(len(txs), 2)


if __name__ == '__main__':
    unittest.main()
