#!/usr/bin/python

import binascii
import lz4f
import struct
import sys

if sys.version_info.major >= 3:
    from builtins import open as _open
else:
    from __builtin__ import open as _open


class Lz4File:
    def __init__(self, name, fileObj=None, seekable=True):
        parseMagic = lambda x: binascii.hexlify(x[:4])
        self.name = name
        if fileObj:
            self.fileObj = fileObj
            self.compEnd = self.tell_end()
        else:
            return open(name)
        self.header = fileObj.read(7)
        if parseMagic(self.header) == b'04224d18':
            self.dCtx = lz4f.createDecompContext()
            self.fileInfo = lz4f.getFrameInfo(self.header, self.dCtx)
            self.blkSizeID = self.fileInfo.get('blkSize')
        else:
            raise IOError
        if seekable:
            try:
                self.load_blocks()
            except:
                print('Unable to load blockDict. Possibly not a lz4 file.')
                raise IOError

    @classmethod
    def open(cls, name=None, fileObj=None, seekable=True):
        if not name and not fileObj:
            sys.stderr.write('Nothing to open!')
        if not fileObj:
            fileObj = _open(name, 'rb')
        return cls(name, fileObj, seekable)

    def close(self):
        self.fileObj.close()

    def decompress(self, outName):
        """
        :type string: outName
        Generic decompress function. Will decompress the entire file to
        outName.
        """
        writeOut = _open(outName, 'wb')
        for blk in self.blkDict.values():
            out = self.read_block(blk=blk)
            writeOut.write(out)
            writeOut.flush()
        writeOut.close()

    def get_block_size(self):
        """
        :type file: fileObj - At least seeked to 7 (past header)
        Static method to determine next block's blockSize.
        """
        size = struct.unpack('<I', self.fileObj.read(4))[0]
        self.fileObj.seek(self.fileObj.tell()-4)
        returnSize = (size & 0x7FFFFFFF)
        if not returnSize:
            return 0
        return returnSize+4

    def load_blocks(self):
        """
        Generates the blkDict, making the file seekable. Only one block will
        be decompressed at a time, minimizing memory usage.
        """
        self.blkDict = {}
        total, blkNum, pos = 0, 0, 7
        blkSize = self.get_block_size()
        while blkSize > 0:
            data = self.read_block(blkSize, setCur=False)
            total += len(data)
            self.blkDict.update({blkNum: {'comp_begin': pos,
                                'decomp_e': total, 'blkSize': blkSize}})
            blkNum += 1
            if not self.fileObj.tell() == self.compEnd:
                blkSize = self.get_block_size()
            else:
                break
            pos = self.fileObj.tell()
        self.end = total-1
        del data, total
        self.curBlk = 0
        self.decomp = self.read_block(blk=self.blkDict.get(0))
        self.seek(0)

    def read(self, size=None):
        """
        :type int: size
        File read-like function. If passed a size, it only reads those bytes.
        If not passed a size, it reads the entire file, from the current
        position.
        """
        out = bytes()
        decompOld = self.decompPos
        if size == 0:
            return ''
        if self.pos == self.end:
            raise EOFError("Reached EOF")
        if not size or self.pos+size > self.end:
            size = self.end-self.pos
        newPos = self.pos+size
        if self.decompPos+size > -1:
            out += self.decomp[decompOld:]
            size = size - len(out)
            self.pos = self.curBlkData.get('decomp_e')
            self.curBlk += 1
            self.decomp = self.read_block(blk=self.curBlkData, setCur=False)
            out += self.read(size)
        else:
            out += self.decomp[decompOld:decompOld+size]
            self.pos = newPos
            return out
        return out

    def read_block(self, blkSize=None, blk=None, setCur=True):
        """
        :type int:  blkSize - returned from get_block_size()
        :type dict: blk     - entry from blkDict
        :type bool: setCur  - update current blk var

        Reads the next block, unless provided a blk from blkDict. If provided
        a blk, it will read that specific block.
        """
        if blk:
            self.fileObj.seek(blk.get('comp_begin'))
            blkSize = blk.get('blkSize')
        if not blkSize:
            blkSize = self.get_block_size()
        if blkSize == 0:
            return ''
        if setCur:
            try:
                iteritems = self.blkDict.iteritems
            except AttributeError:
                iteritems = self.blkDict.items
            self.curBlk = [num for num, b in iteritems()
                           if self.fileObj.tell() == b.get('comp_begin')][0]
        if (self.fileObj.tell() + blkSize + 8) == self.compEnd:
            blkSize += 8
            regen = True
        compData = self.fileObj.read(blkSize)
        resultDict = lz4f.decompressFrame(compData, self.dCtx, self.blkSizeID)
        if 'regen' in locals():
            self._regenDCTX()
        return resultDict.get('decomp')

    def seek(self, offset, whence=0):
        """
        :type int: offset
        File seek-like function. Accepts offset. Whence for future improvement,
        but not yet implemented.
        """
        thisBlk = int()
        if not offset:
            blk = self.blkDict.get(0)
        else:
            try:
                iteritems = self.blkDict.iteritems
            except AttributeError:
                iteritems = self.blkDict.items
            thisBlk, blk = [[num, b] for num, b in iteritems()
                            if offset < b.get('decomp_e')][0]
        if self.curBlk == thisBlk:
            self.pos = offset
        else:
            self.curBlk = thisBlk
            self.decomp = self.read_block(blk=blk, setCur=False)
            self.pos = offset

    def tell(self):
        """
        Returns the current position in the 'decompressed' data.
        """
        return self.pos

    def tell_end(self):
        """
        :type file: fileObj
        Determine the end of the compressed file.
        """
        pos = self.fileObj.tell()
        self.fileObj.seek(0, 2)
        end = self.fileObj.tell()
        self.fileObj.seek(pos)
        return end

    def _regenDCTX(self):
        """
        Regenerate the decompression context.
        """
        try:
            lz4f.freeDecompContext(self.dCtx)
            del self.dCtx
            self.dCtx = lz4f.createDecompContext()
            frameInfo = lz4f.getFrameInfo(self.header, self.dCtx)
            lz4f.disableChecksum(self.dCtx)
        except AttributeError:
            self.dCtx = lz4f.createDecompContext()
            frameInfo = lz4f.getFrameInfo(self.header, self.dCtx)
            pass
        del frameInfo

    @property
    def decompPos(self):
        return self.pos - self.curBlkData.get('decomp_e')

    @property
    def curBlkData(self):
        return self.blkDict.get(self.curBlk)

    def seekable(self):
        if self.blkDict:
            return True
        return False
