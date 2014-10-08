#!/usr/bin/env python

import argparse
import os
import sys

try:
    import lz4tools
except ImportError:
    import __init__ as lz4tools

def getFileInfo(name):
    dCtx = lz4tools.lz4f.createDecompContext()
    with open(name, 'rb') as inFile:
        header = inFile.read(7)
    print(lz4tools.lz4f.getFrameInfo(header, dCtx))

parser=argparse.ArgumentParser()

parser.add_argument('-f', action='store_true', dest='file',   default=False,
                    help='Compress file. Default action if input is a file.')
parser.add_argument('-t', action='store_true', dest='tar',    default=False,
                    help=''.join(['Compress directory to .tar.lz4. ',
                                  'Default action if input is a directory']))
parser.add_argument('-d', action='store_true', dest='decomp', default=False,
                    help=''.join(['Decompress file. Default action if the file ',
                                  'ends in .lz4.']))
parser.add_argument('-i', action='store_true', dest='info', default=False,
                    help=''.join(['Print frame information from the file\'s ',
                                  'header.']))
parser.add_argument('-bs', action='store', dest='blkSizeId', default=7, type=int,
                    help=''.join(['Specify blkSizeId. Valid values are 4-7. ',
                                  'Default value is 7.']), choices=range(4, 8)),
parser.add_argument('-bm', action='store', dest='blkMode', default=0, type=int,
                    help=''.join(['Specify blkMode. 0 = Chained blocks. ',
                                  '1 = Independent blocks Default value is 0.']),
                    choices=[0, 1])
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

#print('blockSizeId: {}'.format(res.blkSizeId))
prefs = lz4tools.lz4f.makePrefs(res.blkSizeId, res.blkMode)

compFile = lambda: lz4tools.compressFileDefault(res.input, outname=res.output, prefs=prefs)
compDir = lambda: lz4tools.compressTarDefault(res.input, outname=res.output)
decompFile = lambda: lz4tools.decompressFileDefault(res.input, outname=res.output)
outErr = lambda: sys.stdout.write('Please specify only ony of the comp/decomp options')

if res.info:
    getFileInfo(res.input)
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
