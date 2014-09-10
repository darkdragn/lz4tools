#!/usr/bin/python

import __builtin__
import lz4
import struct
import sys

class Lz4File:
    MAGIC = '0x184d2204'
    blkDict = {}
    def __init__(self, name, fileObj=None):
        self.lz4sd = lz4.Lz4sd_t()
        self.name = name
        if fileObj:
            self.fileObj = fileObj
            self.end = tell_end(fileObj)
        else:
            return open(name)
    @classmethod
    def open(cls, name = None, fileObj = None):
        if not name and not fileObj:
            sys.stderr.write('Nothing to open!')
        fileObj = __builtin__.open(name)
        magic = struct.unpack('<I', fileObj.read(4))[0]
        if not cls.MAGIC == hex(magic):
             sys.stderr.write('Invalid magic number!')

        des = fileObj.read(3)

        cls.version    = (ord(des[0]) >> 6) & 3   # 2 bits
        cls.blkIndepen = (ord(des[0]) >> 5) & 1   # 1 bit
        cls.blkChk     = (ord(des[0]) >> 4) & 1   # 1 bit
        cls.streamSize = (ord(des[0]) >> 3) & 1   # 1 bit
        cls.streamChk  = (ord(des[0]) >> 2) & 1   # 1 bit
        cls.reserved1  = (ord(des[0]) >> 1) & 1   # 1 bit
        cls.dictionary = (ord(des[0]) >> 0) & 1   # 1 bit

        cls.reserved2  = (ord(des[1]) >> 7) & 1   # 1 bit
        cls.blkSizeID  = (ord(des[1]) >> 4) & 7   # 3 bits
        cls.reserved3  = (ord(des[1]) >> 0) & 15  # 4 bits

        cls.chkBits    = (ord(des[2]) >> 0) & 255 # 8 bits

        return cls(name, fileObj)
    def read_block(self, blkSize = None, uncomp_flag = None,
                   blk = None, setCur = True):
        if blk:
            self.fileObj.seek(blk.get('compressed_begin'))
            blkSize = blk.get('blkSize')
            uncomp_flag = blk.get('uncomp_flag')
        if not blkSize: blkSize, uncomp_flag = get_block_size(self.fileObj)
        if blkSize == 0: return ''
        if setCur:
            self.curBlk = [num for num, b in self.blkDict.iteritems()
                           if self.fileObj.tell() == b.get('compressed_begin')][0]
            #self.pos = self.curBlkData.get('decomp_e')
        compData = struct.unpack('<%ds' % blkSize,
                                 self.fileObj.read(blkSize))[0]
        if uncomp_flag:
            return compData
        else:
            return lz4.uncompress_continue(compData, self.lz4sd,
                                           self.blkSizeID)
    def read(self, size = -1):
        out = str()
        if self.seekable:
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
        else:
            pos=self.fileObj.tell()
            while pos+4 < self.end:
                out += self.read_block()
                pos = self.fileObj.tell()
        return out
    def decompress(self, outName):
        pos = self.fileObj.tell()
        if not self.seekable:
            self.fileObj.seek(7)
        writeOut = __builtin__.open(outName, 'wb')
        for blk in self.blkDict.values():
            out = self.read_block(blk=blk)
            writeOut.write(out)
            writeOut.flush()
        writeOut.close()
        self.fileObj.seek(pos)
    def load_blocks(self):
        startPos = self.fileObj.tell()
        total, blkNum, decomp, pos = 0, 0, 0, 11
        blkSize, uncomp_flag = get_block_size(self.fileObj)
        while blkSize > 0:
            data = self.read_block(blkSize, uncomp_flag, setCur=False)
            total += len(data)
            self.blkDict.update({blkNum: {'compressed_begin': pos,
                                'decomp_e': total, 'blkSize': blkSize,
                                'uncomp_flag': uncomp_flag}})
            blkNum += 1
            blkSize, uncomp_flag = get_block_size(self.fileObj)
            pos = self.fileObj.tell()
        del data, total
        self.curBlk = 0
        self.seek(0)
        self.fileObj.seek(startPos)
    def seek(self, offset, whence=0):
        if not offset:
            blk = self.blkDict.get(0)
        else:
            self.curBlk, blk = [[num, b] for num, b in self.blkDict.iteritems()
                   if offset < b.get('decomp_e')][0]
        self.decomp =  self.read_block(blk = blk, setCur=False)
        self.pos = offset
    def tell(self):
        return self.pos
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
def get_block_size(fileObj):
    size = struct.unpack('<I', fileObj.read(4))[0]
    return size & 0x7FFFFFFF, size >> 31
def open(name):
    return Lz4File.open(name)
def tell_end(fileObj):
    pos = fileObj.tell()
    fileObj.seek(0, 2)
    end = fileObj.tell()
    fileObj.seek(pos)
    return end
