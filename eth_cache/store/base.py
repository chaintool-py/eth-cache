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
