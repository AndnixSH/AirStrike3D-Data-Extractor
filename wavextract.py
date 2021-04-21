#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import struct

RIFF_MAGIC = b'RIFF'
RIFF_LENGTH = struct.Struct('<I')


def main():
    in_file = sys.argv[1]

    # Since the files are tiny lets cheat again and just read the entire thing.
    with open(in_file, 'rb') as fin:
        in_file = fin.read()

    offset = 0
    count = 0

    # We're going to skim through the file looking for the start of a RIFF file.
    while True:
        start = in_file.find(RIFF_MAGIC, offset)
        if start == -1:
            # None left, so we're done with this .apk.
            print('Extracted {0} files.'.format(count))
            return

        # Found one, so lets read the next 4 bytes which are the length of the RIFF file.
        length = RIFF_LENGTH.unpack_from(in_file, start + 4)[0]
        # The 8 comes from the 4 bytes for RIFF and the 4 bytes for the length
        # itself, which aren't included in the length.
        offset = start + 8 + length

        # annnnd save it.
        with open('wav_{0}.wav'.format(count), 'wb') as fout:
            fout.write(in_file[start:offset])

        count += 1

if __name__ == '__main__':
    sys.exit(main())