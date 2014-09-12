#!/usr/bin/python

import lz4f, struct, time

def readNextBlock(fileObj, dCtx, blkId):
    decompString = ''
    blkSize = struct.unpack('<I', fileObj.read(4))[0]+4
    fileObj.seek(fileObj.tell()-4)
    compressedString = fileObj.read(blkSize)
    decompString = lz4f.decompressFrame(compressedString, test, blkId)
    return decompString
def testDecomp(fileObj, dCtx, blkId):
    start = f.tell()
    decompString = readNextBlock(fileObj, dCtx, blkId)
    end = f.tell()
    decompLen = len(decompString)
    print 'Block check, start: %i, end: %i, decompressedLen: %i' % (start,
                                                                    end, decompLen)

test = lz4f.createDecompContext()
f=open('../../../lz4file.tar.lz4')
header = f.read(7)
blkId = lz4f.getFrameInfo(header, test)
testDecomp(f, test, blkId)
testDecomp(f, test, blkId)
testDecomp(f, test, blkId)
f.seek(7)
testDecomp(f, test, blkId)
