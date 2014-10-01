import lz4file
import os
import tarfile
import StringIO
import unittest

class TestLZ4File(unittest.TestCase):

    #def test_random(self):
    #  DATA = os.urandom(128 * 1024)  # Read 128kb
    #  self.assertEqual(DATA, lz4.loads(lz4.dumps(DATA)))
    
    def test_1_write(self):
        buff = StringIO.StringIO()
        tarBuff = tarfile.open(fileobj=buff, mode='w|')
        tarBuff.add('src')
        tarBuff.close()
        buff.seek(0)
        with open('src.lz4', 'w|') as output:
            output.write(lz4file.lz4f.compressFrame(buff.read()))
            output.flush()
            output.close()
        self.assertTrue(os.path.exists('src.lz4'))
    
    def test_2_file(self):
        testTar = lz4file.openTar('src.lz4')
        count = testTar.getmembers()
        for root, dirs, files in os.walk('src'):
            dircount = 1
            dircount += len(dirs)
            dircount += len(files)
        self.assertEqual(dircount, len(count))
        os.remove('src.lz4')

if __name__ == '__main__':
    unittest.main()

