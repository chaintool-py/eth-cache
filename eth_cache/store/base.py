# external imports
from chainlib.eth.tx import pack
import json
from hexathon import strip_0x

# local imports
from . import StoreAction

class Store:
    
    def __init__(self, chain_spec, cache_root, address_rules=None):
        self.chain_spec = chain_spec
        self.address_rules = address_rules
        self.adder = {}


    def register_adder(self, action, adder):
        if self.adder.get(action) != None:
            raise ValueError('Already added action ' + action.value)
        self.adder[action] = adder


    def add(self, action, k, v):
        return self.adder[action].add(k, v)


    def to_filepath(self, action, v):
        return self.adder[action].to_filepath(v)


    def put_tx(self, tx, include_data=False):
        raw = pack(tx.src, self.chain_spec)
        #tx_hash_dirnormal = strip_0x(tx.hash).upper()
        tx_hash_dirnormal = strip_0x(tx.hash)
        tx_hash_bytes = bytes.fromhex(tx_hash_dirnormal)
        #self.tx_raw_dir.add(tx_hash_bytes, raw)
        self.add(StoreAction.TX_RAW, tx_hash_bytes, raw)
        addresses = []
        if self.address_rules != None:
            for a in tx.outputs + tx.inputs:
                if a not in addresses:
                    addresses.append(a)
        else:
            for a in tx.outputs + tx.inputs:
                addresses.append(a)

        if include_data:
            src = json.dumps(tx.src).encode('utf-8')
            #self.tx_dir.add(bytes.fromhex(strip_0x(tx.hash)), src)
            self.add(StoreAction.TX, bytes.fromhex(strip_0x(tx.hash)), src)
    
            if tx.result != None:
                rcpt_src = tx.result.src
                rcpt_src = json.dumps(rcpt_src).encode('utf-8')
                #self.rcpt_dir.add(bytes.fromhex(strip_0x(tx.hash)), rcpt_src)
                self.add(StoreAction.RCPT, bytes.fromhex(strip_0x(tx.hash)), rcpt_src)

        for a in addresses:
            self.put_address(tx, a)


    def put_address(self, tx, address):
        raise NotImplementedError()
