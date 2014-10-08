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
            try:
                fileobj = Lz4File.open(name)
                #fileobj=__builtin__.open(name, 'rb')
            except IOError:
                raise ReadError('Not a lz4 file')
        elif not name and not fileobj:
            print('Unable to open without a name or fileobj')
            return
        if not name and hasattr(fileobj.name):
            name = fileobj.name
        try:
            t = cls(None, mode, fileobj)
        except:
            fileobj.close()
        t._extfileobj = False
        return t
    #tarfile.TarFile.OPEN_METH.update({'lz4': 'lz4open'})
    #tarfile.TarFile.lz4open = lz4open
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open",   # bzip2 compressed tar
        "lz4": "lz4open"    # lz4 compressed tar
        }