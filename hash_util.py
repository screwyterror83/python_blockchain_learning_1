#!"D:\Program Files\CodeLanguage\Python\Python37\python.exe"


from hashlib import sha256
from json import dumps

def hash_string_256(string):
    return sha256(string).hexdigest()


def hash_block(block):
    # Use hashlib sha265 and json package to hash the block as string, and transcode to utf-8 and output to readable charactors instead of binary numbers
    return hash_string_256(dumps(block, sort_keys=True).encode())
