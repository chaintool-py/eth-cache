# standard imports
import tempfile
import shutil
import unittest

# external imports
from chainlib.chain import ChainSpec
from chainlib.eth.gas import (
        Gas,
        OverrideGasOracle,
        )
from chainlib.eth.nonce import RPCNonceOracle
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
from chainlib.eth.dialect import DialectFilter as EthDialectFilter

from chainlib.eth.unittest.ethtester import EthTesterCase

# TODO: 2024-06-16 suddenly state_root value is binary, which breaks the json serializer. this seems to be a bug in the eth-tester, and this code should probably be moved to chainlib-eth unittest and implemented by default in test cases
class DialectFilter(EthDialectFilter):
    
    def apply_src(self, src, dialect_filter=None):

        for k in src.keys():
            if type(src[k]) == bytes:
                src[k] = '0x' + src[k].hex()

        return src


class TestCache(EthTesterCase):

    def setUp(self):
        super(TestCache, self).setUp()
        fp = tempfile.mkdtemp()
        self.cache_dir = fp

        class Applier:
            def apply_rules_addresses(self, sender, recipient, address):
                return True

        self.address_rules = Applier()
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

        fltr = DialectFilter()
        self.block = Block(block_src, dialect_filter=fltr)
        self.tx = Tx(tx_src, block=self.block, rcpt=rcpt_src, dialect_filter=fltr)
