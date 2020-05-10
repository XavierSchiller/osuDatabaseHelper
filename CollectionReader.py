import functools


def _leb128_dumps(value, signed=False):
    """
    Encode a number using LEB128 encoding.
    :param int value: the value to encode
    :param bool signed: whether to use a signed LEB128 representation
    :return: encoded value
    :rtype: bytes
    """

    if not signed and value < 0:
        raise ValueError("Value cannot be negative.")

    buf = bytearray()
    more = True

    while more:

        # Obtain the lowest 7 bits, and shift the remainder.
        byte = value & 0x7f
        value >>= 7

        # For signed numbers, use sign extension to ensure that the
        # MSB is 0 for positive numbers, and 1 for negative numbers.
        if signed:
            if value == 0 and byte & 0x40 == 0:
                # Last byte for positive number
                more = False
            elif value == -1 and byte & 0x40:
                # Last byte for negative number
                more = False
            else:
                # Not done yet
                byte |= 0x80

        # Unsigned numbers do not have a sign bit.
        else:
            if value:
                # Not done yet
                byte |= 0x80
            else:
                more = False

        buf.append(byte)

    return bytes(buf)


def leb128_dump(value, fp, signed=False, max=None):
    """Like leb128_dump(), but writes to a file-like object."""
    fp.write(_leb128_dumps(value, signed=signed))

def _leb128_load(iterable, signed=False, max=None):
    """Internal LEB128 decoding routine"""
    decoded = 0
    shift = 0

    # The 'iterable' must yield int values
    size = 0
    for size, byte in enumerate(iterable, 1):
        decoded |= (byte & 0x7f) << shift
        shift += 7
        if byte & 0x80 == 0:
            break

        if max == size:  # this also works if max=None
            raise ValueError(
                "encoded value seems to be >{0:d} bytes".format(size))

    else:
        # Reached when no 'break' was issued in the loop above.
        raise ValueError("truncated value after {0:d} bytes".format(size))

    # Negative numbers have a sign bit in the last byte.
    if signed and byte & 0x40:
        decoded -= (1 << shift)

    return decoded, size


def leb128_load(fp, signed=False, max=None, only_value=True):
    """
    Like leb128_loads(), but reads from a file-like object.
    This returns only the value, not the number of bytes read.
    """
    single_bytes_reader = map(ord, iter(functools.partial(fp.read, 1), b''))
    result = _leb128_load(single_bytes_reader, signed=signed, max=max)
    return result[0] if only_value else result

def readUTF8AfterLEB(f, length):
    b = bytearray()
    for _ in range(length):
        y = int.from_bytes(f.read(1),"little")
        b.append(y)
    return b.decode('utf-8')
    
getInt = lambda x,y: int.from_bytes(x.read(y), "little")

def readString(f) -> str:
    isLEB = getInt(f,1)
    if isLEB == 11:
        length = leb128_load(f)
        return readUTF8AfterLEB(f, length)
    else:
        return "" 

with open('collection.db', mode="rb") as f:
    version = getInt(f,4)
    CollT = getInt(f,4)
    print(version, CollT)
    for _ in range(CollT):
        string = readString(f)
        numberOfMaps = getInt(f,4)
        print(string, numberOfMaps)
        for __ in range(numberOfMaps):
            mapHash = readString(f)
            print(mapHash)
