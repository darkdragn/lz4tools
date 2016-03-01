#!/usr/bin/env python

import argparse
import os
import sys

try:
    import lz4tools
except ImportError:
    import __init__ as lz4tools


def compFile():
    return lz4tools.compressFileDefault(res.input, outname=res.output)


def compDir():
    return lz4tools.compressTarDefault(res.input, outname=res.output)


def decompFile():
    return lz4tools.decompressFileDefault(res.input, outname=res.output)


def outErr():
    return sys.stdout.write(''.join(['Please specify only ony of the ',
                                    'comp/decomp options']))

parser = argparse.ArgumentParser()

parser.add_argument('-f', action='store_true', dest='file',   default=False,
                    help='Compress file. Default action if input is a file.')
parser.add_argument('-t', action='store_true', dest='tar',    default=False,
                    help=''.join(['Compress directory to .tar.lz4. ',
                                  'Default action if input is a directory']))
parser.add_argument('-d', action='store_true', dest='decomp', default=False,
                    help=''.join(['Decompress file. Default action if the',
                                  'file ends in .lz4.']))
parser.add_argument('-i', action='store_true', dest='info', default=False,
                    help=''.join(['Print frame information from the file\'s ',
                                  'header.']))
parser.add_argument('-bs', action='store', dest='blkSizeId', default=7,
                    type=int, help=''.join(['Specify blkSizeId. Valid values',
                                            'are 4-7. Default value is 7.']),
                    choices=range(4, 8))
parser.add_argument('-bm', action='store', dest='blkMode', default=0, type=int,
                    help=''.join(['Specify blkMode. 0 = Chained blocks. ',
                                  '1 = Independent blocks Default value is',
                                  '0.']), choices=[0, 1])
parser.add_argument('input', action='store', help='The targeted input.')
parser.add_argument('output', action='store', nargs='?', default=None,
                    help='Optional output target.')
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()
res = parser.parse_args()

prefs = lz4tools.lz4f.makePrefs(res.blkSizeId, res.blkMode)
kwargs = {'name': res.input, 'outname': res.output, 'prefs': prefs}


def compFile():
    return lz4tools.compressFileDefault(**kwargs)


def compDir():
    return lz4tools.compressTarDefault(**kwargs)


def decompFile():
    return lz4tools.decompressFileDefault(res.input, outname=res.output)


def getInfo():
    return lz4tools.getFileInfo(res.input)


def outErr():
    return sys.stdout.write(''.join(['Please specify only ony of the ',
                                     'comp/decomp options']))


if res.info:
    print(getInfo())
elif res.file:
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
