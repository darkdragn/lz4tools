import __builtin__
import tarfile
from lz4file import Lz4File
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
