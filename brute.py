import sys
import warnings
from cStringIO import StringIO

from PIL import Image

FOOTER = b'TRUEVISION-XFILE'


def main():
    in_file = sys.argv[1]

    with open(in_file, 'rb') as fin:
        in_file = fin.read()

    start = in_file.find(FOOTER)
    # Ends with a '.' then 0x00.
    end = start + len(FOOTER) + 2

    count = 0
    greatest_found_idx = None
    while count < len(in_file):
        attempted_tga = StringIO(in_file[end-count:end])

        try:
            with warnings.catch_warnings(record=True) as w:
                i = Image.open(attempted_tga)
                if len(w):
                    continue
        except IOError:
            pass
        else:
            greatest_found_idx = end - count
        finally:
            count += 1

    print(greatest_found_idx)
    i.save('image.png')


if __name__ == '__main__':
    sys.exit(main())