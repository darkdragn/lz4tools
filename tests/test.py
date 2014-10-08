import lz4f
import lz4tools
import os
import unittest

class TestLZ4File(unittest.TestCase):

    def test_1_writeTar(self):
        lz4tools.compressTarDefault('src')
        self.assertTrue(os.path.exists('src.tar.lz4'))
    
    def test_2_readTar(self):
        testTar = lz4tools.openTar('src.tar.lz4')
        count = testTar.getmembers()
        testTar.close()
        dircount = 1
        for root, dirs, files in os.walk('src'):
            dircount += len(dirs)
            dircount += len(files)
        self.assertEqual(dircount, len(count))
        os.remove('src.tar.lz4')

    def test_3_prefs(self):
        cCtx = lz4f.createCompContext()
        dCtx = lz4f.createDecompContext()
        prefs = lz4f.makePrefs(5)
        header = lz4f.compressBegin(cCtx, prefs)
        frameInfo = lz4f.getFrameInfo(header, dCtx)
        self.assertEqual(5, frameInfo.get('blkSize'))


if __name__ == '__main__':
    unittest.main()

