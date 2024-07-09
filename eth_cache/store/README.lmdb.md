# Storage paths


## Content prefixes

| file cache path | lmdb cache key | content |
|---|---|---|
| `block/src/<block_hash_hex_leveldir>` | `block/src/<block_hash_bytes>` | block json source |
| `block/num/<block_number_int_leveldir>` | `block/num/<block_number_int_bytes_be>` | block hash (32 bytes) |
| `block/hash/<block_hash_hex_leveldir>` | `block/hash/<block_hash_bytes>` | block number (8 bytes) |
| `tx/src/<tx_hash>` | `tx/src/<tx_hash_bytes>` | tx json source | 
| `tx/raw/<tx_hash>` | `tx/raw/<tx_hash_bytes>` | tx rlp (bytes) |
| `rcpt/src/<tx_hash>` | `rcpt/src/<tx_hash_bytes>` | tx receipt json source |
| `address/<address_hex_leveldir>/<tx_hash_hex>` | `address/<address_bytes>/<tx_hash>` | none |

The address index has no content, and it has one key/file per transaction hash associated with the address.

## Leveldir

## hex

Two first bytes became two nested directory named after the byte value.


| value | path |
|---|---|
| `2B10B3DF...BCEF9D9B` | `2B/10/2B10B3DF...BCEF9D9B` |


## number

Two nested directories segment numbers in 100000 and 100 strides respectively.

| number | path |
|---|---|
| 12345678 | 12300000/12345000/12345678 |
| 98654 | 0/98000/98654 |
