#!/usr/bin/python

import __builtin__
import lz4f
import struct
import sys
import tarfile

class Lz4File:
    blkDict = {}
    def __init__(self, name, fileObj=None, seekable=True):
        self.name = name
        if fileObj:
            self.fileObj = fileObj
            self.end = tell_end(fileObj)
        else:
            return open(name)
        self.dCtx = lz4f.createDecompContext()
        self.header = fileObj.read(7)
        self.fileInfo = lz4f.getFrameInfo(self.header, self.dCtx)
        self.blkSizeID = self.fileInfo.get('blkSize')
        if seekable:
            try:
                self.load_blocks()
            except:
                print 'Unable to load blockDict. Possibly not a lz4 file.'
                raise
    @classmethod
    def open(cls, name = None, fileObj = None, seekable=True):
        if not name and not fileObj:
            sys.stderr.write('Nothing to open!')
        if not fileObj:
            fileObj = __builtin__.open(name)
        return cls(name, fileObj, seekable)
    def read_block(self, blkSize = None, blk = None, setCur = True):
        if blk:
            self.fileObj.seek(blk.get('compressed_begin'))
            blkSize = blk.get('blkSize')
        if not blkSize: blkSize = get_block_size(self.fileObj)
        if blkSize == 0: return ''
        if setCur:
            self.curBlk = [num for num, b in self.blkDict.iteritems()
                           if self.fileObj.tell() == b.get('compressed_begin')][0]
        if (self.fileObj.tell() + blkSize + 8) == self.end:
            blkSize += 8
            regen = True
        compData = self.fileObj.read(blkSize)
        resultDict = lz4f.decompressFrame(compData, self.dCtx, self.blkSizeID)
        if regen: self.regenDCTX()
        return resultDict.get('decomp')
    def load_blocks(self):
        total, blkNum, pos = 0, 0, 7
        blkSize = get_block_size(self.fileObj)
        while blkSize > 0:
            data = self.read_block(blkSize, setCur=False)
            total += len(data)
            self.blkDict.update({blkNum: {'compressed_begin': pos,
                                'decomp_e': total, 'blkSize': blkSize}})
            blkNum += 1
            if not self.fileObj.tell() == self.end:
                blkSize = get_block_size(self.fileObj)
            else:
                break
            pos = self.fileObj.tell()
        del data, total
        self.curBlk = 0
        self.decomp = self.read_block(blk=self.blkDict.get(0))
        self.seek(0)
    def read(self, size = -1):
        out = str()
        decompOld = self.decompPos
        newPos = self.pos+size
        if self.decompPos+size > -1:
            out += self.decomp[decompOld:]
            size = size - len(out)
            self.pos = self.curBlkData.get('decomp_e')
            self.curBlk +=1
            self.decomp = self.read_block(blk=self.curBlkData, setCur=False)
            out += self.read(size)
        else:
            out += self.decomp[decompOld:decompOld+size]
            self.pos = newPos
            return out
        return out
    def decompress(self, outName):
        writeOut = __builtin__.open(outName, 'wb')
        for blk in self.blkDict.values():
            out = self.read_block(blk=blk)
            writeOut.write(out)
            writeOut.flush()
        writeOut.close()
    def seek(self, offset, whence=0):
        thisBlk = int()
        if not offset:
            blk = self.blkDict.get(0)
        else:
            thisBlk, blk = [[num, b] for num, b in self.blkDict.iteritems()
                   if offset < b.get('decomp_e')][0]
        if self.curBlk == thisBlk:
            self.pos = offset
        else:
            self.curBlk = thisBlk
            self.decomp =  self.read_block(blk = blk, setCur=False)
            self.pos = offset
    def tell(self):
        return self.pos
    def regenDCTX(self):
        try:
            del self.dCtx
        except AttributeError:
            pass
        self.dCtx = lz4f.createDecompContext()
        frameInfo = lz4f.getFrameInfo(self.header, self.dCtx)
        del frameInfo
    @property
    def decompPos(self):
        return self.pos - self.curBlkData.get('decomp_e')
    @property
    def curBlkData(self):
        return self.blkDict.get(self.curBlk)
    @property
    def seekable(self):
        if self.blkDict:
            return True
        return False

class Lz4Tar(tarfile.TarFile):
    @classmethod
    def lz4open(cls, name=None, mode='r', fileobj=None):
        if name and not fileobj:
            fileobj=__builtin__.open(name)
        elif not name and not fileobj:
            print 'Unable to open without a name or fileobj'
            return
        if not name and hasattr(fileobj.name):
            name = fileobj.name
        lz4FileOut = Lz4File.open(fileObj=fileobj)
        return cls(None, mode, lz4FileOut)
    tarfile.TarFile.OPEN_METH.update({'lz4': 'lz4open'})

# Generic lz4file methods
def get_block_size(fileObj):
    size = struct.unpack('<I', fileObj.read(4))[0]
    fileObj.seek(fileObj.tell()-4)
    returnSize = (size & 0x7FFFFFFF)
    if not returnSize:
        return 0
    return returnSize+4
def open(name=None, fileObj=None):
    return Lz4File.open(name, fileObj)
def openTar(name=None, fileObj=None):
    return Lz4Tar.lz4open(name, 'r', fileObj)
def tell_end(fileObj):
    pos = fileObj.tell()
    fileObj.seek(0, 2)
    end = fileObj.tell()
    fileObj.seek(pos)
    return end
