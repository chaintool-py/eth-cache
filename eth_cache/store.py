# standard imports
import logging
import os

# external imports
from hexdir import HexDir
from chainlib.eth.tx import pack
from hexathon import strip_0x

logg = logging.getLogger(__name__)


class PointerHexDir(HexDir):
    
    def __init__(self, root_path, key_length, levels=2, prefix_length=0):
        super(PointerHexDir, self).__init__(root_path, key_length, levels, prefix_length)
        self.pointers = {}


    def register_pointer(self, label, dir_name=None):
        if dir_name == None:
            dir_name = label
        pointer_dir = os.path.join(self.path, dir_name)
        os.makedirs(pointer_dir, exist_ok=True)

        label_file = os.path.join(pointer_dir, '.label')
        try:
            os.stat(label_file)
        except FileNotFoundError:
            f = open(label_file, 'w')
            f.write(label)
            f.close()

        self.pointers[label] = pointer_dir


    def add_pointer(self, pointer, pointer_relpath, destination_path):
        if isinstance(pointer_relpath, list):
            link_path = os.path.join(self.pointers[pointer], *pointer_relpath)
        else:
            link_path = os.path.join(self.pointers[pointer], pointer_relpath)
        os.makedirs(os.path.dirname(link_path), exist_ok=True)
        os.symlink(destination_path, link_path)
        logg.debug('added link {} -> {}'.format(link_path, destination_path))


    def add(self, key, content, prefix=b'', pointers={}):
        (c, entry_path) = super(PointerHexDir, self).add(key, content, prefix=prefix)
        for k in pointers.keys():
            self.add_pointer(k, pointers[k], entry_path)


class TxFileStore:

    def __init__(self, chain_spec, backend):
        self.backend = backend 
        self.chain_spec = chain_spec


    def put(self, block, tx, addresses, attrs={}):
        for address in addresses:
            tx_src = tx.as_dict()
            tx_raw = pack(tx_src, self.chain_spec)
            filename = '{}_{}_{}'.format(block.number, tx.index, strip_0x(tx.hash))
            self.backend.add(bytes.fromhex(tx.hash), tx_raw, pointers={'address': [strip_0x(address),filename]})
