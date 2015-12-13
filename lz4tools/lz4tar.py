import sys
import tarfile
if sys.version_info.major >= 3:
    from .lz4file import Lz4File
else:
    from lz4file import Lz4File


class Lz4Tar(tarfile.TarFile):
    @classmethod
    def lz4open(cls, name, mode='r', fileobj=None, **kwargs):
        try: 
            import lz4tools
            Lz4File = lz4tools.Lz4File
        except (ImportError, AttributeError):
            raise CompressionError("Lz4file module is not available")
        if name and fileobj is None:
            try:
                fileobj = Lz4File.open(name)
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
    tarfile.TarFile.OPEN_METH.update({'lz4': 'lz4open'})
    tarfile.TarFile.lz4open = lz4open
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open",   # bzip2 compressed tar
        "lz4": "lz4open"    # lz4 compressed tar
        }
