#!/usr/bin/env python

import argparse
import os
import sys

try:
    import lz4tools
except ImportError:
    import __init__ as lz4tools

parser=argparse.ArgumentParser()

parser.add_argument('-f', action='store_true', dest='file',   default=False,
                    help='Compress file. Default action if input is a file.')
parser.add_argument('-t', action='store_true', dest='tar',    default=False,
                    help=''.join(['Compress directory to .tar.lz4. ',
                                  'Default action if input is a directory']))
parser.add_argument('-d', action='store_true', dest='decomp', default=False,
                    help=''.join(['Decompress. Default action if the file ends',
                                  ' in .lz4.']))
parser.add_argument('input', action='store', help='The targeted input.')
parser.add_argument('output', action='store', nargs='?', default=None,
                    help='Optional output target.')
#parser.add_argument('-dt', action='store_true', dest='decompTar',
#                  help=''.join(['Decompress tar. Default action if the file',
#                                ' ends in .tar.lz4.']))
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()
res = parser.parse_args()

compFile = lambda: lz4tools.compressFileDefault(res.input, outname=res.output)
compDir = lambda: lz4tools.compressTarDefault(res.input, outname=res.output)
decompFile = lambda: lz4tools.decompressFileDefault(res.input, outname=res.output)
outErr = lambda: sys.stdout.write('Please specify only ony of the comp/decomp options')

if res.file:
    if res.tar or res.decomp:
        outErr()
    compFile()
elif res.tar:
    if res.decomp:
        outErr()
    compDir()
elif res.input.endswith('lz4'):
    decompFile()
elif os.path.isfile(res.input):
    compFile()
elif os.path.isdir(res.input):
    compDir()
else:
    parser.print_help()
