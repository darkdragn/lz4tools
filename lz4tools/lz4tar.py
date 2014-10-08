import sys
import tarfile
if sys.version_info.major >= 3:
    import builtins as __builtin__
    from .lz4file import Lz4File
else:
    import __builtin__
    from lz4file import Lz4File

class Lz4Tar(tarfile.TarFile):
    @classmethod
    def lz4open(cls, name=None, mode='r', fileobj=None):
        if name and not fileobj:
            fileobj=__builtin__.open(name, 'rb')
        elif not name and not fileobj:
            print('Unable to open without a name or fileobj')
            return
        if not name and hasattr(fileobj.name):
            name = fileobj.name
        lz4FileOut = Lz4File.open(fileObj=fileobj)
        try:
            t = cls(None, mode, lz4FileOut)
        except:
            lz4FileOut.close()
        t._extfileobj = False
        return t
    tarfile.TarFile.OPEN_METH.update({'lz4': 'lz4open'})
    tarfile.TarFile.lz4open = lz4open
