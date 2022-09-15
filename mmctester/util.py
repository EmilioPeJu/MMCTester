#!/usr/bin/env python

import binascii


def hex_to_bin(hex_data):
    ALLOWED_HEX = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                       'a', 'b', 'c', 'd', 'e', 'f'])
    stripped = ''.join(item for item in hex_data if item in ALLOWED_HEX)
    return binascii.unhexlify(stripped)


def chunk_string(string, width):
    for i in range(0, len(string), width):
        yield string[i:i+width]
