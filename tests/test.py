import lz4tools
import os
import unittest


class TestLZ4File(unittest.TestCase):

    def test_1_write(self):
        lz4tools.compressTarDefault('src')
        self.assertTrue(os.path.exists('src.tar.lz4'))

    def test_2_file(self):
        testTar = lz4tools.openTar('src.tar.lz4')
        count = testTar.getmembers()
        testTar.close()
        dircount = 1
        for root, dirs, files in os.walk('src'):
            dircount += len(dirs)
            dircount += len(files)
        self.assertEqual(dircount, len(count))
        os.remove('src.tar.lz4')

if __name__ == '__main__':
    unittest.main()
