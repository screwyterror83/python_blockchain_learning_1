
from hashlib import sha256
from json import dumps


def hash_string_256(string):
    return sha256(string).hexdigest()


def hash_block(block):
    # Use hashlib sha265 and json package to hash the block as string,
    # and transcode to utf-8 and output to readable charactors
    # instead of binary numbers
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [
        tx.to_ordered_dict() for tx in hashable_block['transactions']
        ]
    return hash_string_256(dumps(hashable_block, sort_keys=True).encode())
