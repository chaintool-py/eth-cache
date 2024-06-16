# standard imports
import enum


class StoreAction(enum.Enum):
    BLOCK = 'block/src'
    BLOCK_NUM = 'block/num'
    BLOCK_HASH = 'block/hash'
    TX = 'tx/src'
    TX_RAW = 'tx/raw'
    RCPT = 'rcpt/src'
    RCPT_RAW = 'rcpt/raw'
    ADDRESS = 'address'
