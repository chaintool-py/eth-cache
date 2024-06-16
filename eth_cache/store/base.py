class Store:
    
    def __init__(self, chain_spec, cache_root, address_rules=None):
        self.chain_spec = chain_spec
        self.address_rules = address_rules
