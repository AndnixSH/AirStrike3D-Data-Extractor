#!/usr/bin/env python
# -*- utf-8 -*-
import sys
import struct


class PakParser(object):
    #: File prefix.
    MAGIC_NUMBER = b'\x00\x00\x80\x3F\x99\x99\x00\x00'
    TABLE_ENTRY_SIZE = 76

    def __init__(self):
        self.file_count = 0
        self.cipher_table = None
        self.file_table = {}

    def load(self, file_obj):
        if not file_obj.read(len(self.MAGIC_NUMBER)) == self.MAGIC_NUMBER:
            raise IOError('invalid magic number')

        # The start of the file listing table (given from the start of the
        # file) and the number of file entries.
        file_table_offset, self.file_count = struct.unpack(
            '<II',
            file_obj.read(8)
        )

        # The cipher table comes after the header fields and is always exactly
        # 1kb.
        self.cipher_table = file_obj.read(1024)

        # Each entry in the file listing table is 76 bytes.
        file_obj.seek(file_table_offset, 0)

        self.file_table = dict(
            (filename.strip('\x00'), (offset, size))
            for filename, offset, size in (
                self.unpack_table_entry(
                    self.decipher(
                        file_obj.read(self.TABLE_ENTRY_SIZE),
                        i * self.TABLE_ENTRY_SIZE
                    )
                )
                for i in xrange(self.file_count)
            )
        )

    def decipher(self, chunk, offset):
        return ''.join(
            chr(
                ord(c)
                ^
                ord(self.cipher_table[(i + offset) % 1024])
            )
            for i, c in enumerate(chunk)
        )

    def unpack_table_entry(self, entry):
        # Filename (64 bytes)
        # Offset (4 bytes)
        # Size (4 bytes)
        # The unknown 4 bytes seem to always be 0.
        return struct.unpack_from('<64sIII', entry)[:3]

    def extract_file(self, file_obj, file_name):
        offset, size = self.file_table[file_name]
        file_obj.seek(offset, 0)
        return file_obj.read(size)


def main():
    with open(sys.argv[1], 'rb') as fin:
        pak = PakParser()
        pak.load(fin)
        print(pak.file_table.keys())
        sys.stdout.write(pak.extract_file(fin, sys.argv[2]))

if __name__ == '__main__':
    sys.exit(main())