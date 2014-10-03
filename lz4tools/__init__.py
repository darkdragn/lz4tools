import __builtin__
import lz4f
import os
import tarfile
from lz4file import Lz4File
from lz4tar import Lz4Tar

def compressFileDefault(name, overwrite=None):
    """
    :type string: name      - name of file to compress
    :type bool:   overwrite - overwrite destination
    Generic compress method for a file. Adds .lz4 to original file name for
    output.

    ***WARNING*** Currently uses lz4f.compressFrame, which will read the entire
    original file into memory, then pass to c-module for compression. Avoid
    using this for large files until migrated to advCompress functions.
    """
    outname = '.'.join([name, 'lz4'])
    if os.path.exists(outname):
        print 'File Exists!'
        pass
    with __builtin__.open(outname, 'w') as out:
        with __builtin__.open(name) as infile:
            out.write(lz4f.compressFrame(infile.read()))
        out.flush()
        out.close()
def compressTarDefault(dirName, overwrite=None):
    """
    :type string: dirName   - the name of the dir to tar
    :type bool:   overwrite - overwrite destination
    Generic compress method for creating .tar.lz4 from a dir.

    ***WARNING*** Currently uses StringIO object until lz4file supports write.
    Avoid using for large directories, it will consume quite a bit of RAM.
    """
    import StringIO
    buff = StringIO.StringIO()
    tarbuff = tarfile.open(fileobj=buff, mode='w|')
    tarbuff.add(dirName)
    tarbuff.close()
    buff.seek(0)
    with __builtin__.open('.'.join([dirName, 'tar', 'lz4']), 'w') as out:
        out.write(lz4f.compressFrame(buff.read()))
        out.flush()
        out.close()
def open(name=None, fileObj=None):
    """  Alias for Lz4File.open()    """
    return Lz4File.open(name, fileObj)
def openTar(name=None, fileObj=None):
    """  Alias for Lz4Tar.open()     """
    return Lz4Tar.lz4open(name, 'r', fileObj)
