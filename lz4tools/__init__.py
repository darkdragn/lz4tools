import lz4f
import os
import sys

if sys.version_info.major >= 3:
    import builtins as __builtin__
    from .lz4file import Lz4File
    from .lz4tar import Lz4Tar
    from io import BytesIO as StringIO
else:
    import __builtin__
    from lz4file import Lz4File
    from lz4tar import Lz4Tar
    from StringIO import StringIO


__all__ = ['lz4file', 'lz4tar']


def compressFileDefault(name, overwrite=False, outname=None, prefs=None):
    """
    :type string: name      - name of file to compress
    :type bool:   overwrite - overwrite destination
    :type string: outname   - name for compressed file, not required.
                              Default will be '.'.join([name, 'lz4'])
    Generic compress method for a file. Adds .lz4 to original file name for
    output, unless outname is provided.

    ***NOTE*** No longer uses compressFrame. This is now large file safe!
    It will now read the input in 64Kb chunks.
    """
    if not outname:
        outname = '.'.join([name, 'lz4'])
    if os.path.exists(outname):
        if not overwrite:
            print('File Exists!')
            return
        print('Overwrite authorized')
    if not os.path.exists(name):
        print('Unable to locate the original file. Please check filename.')
        return
    cCtx = lz4f.createCompContext()
    header = lz4f.compressBegin(cCtx, prefs)
    with __builtin__.open(outname, 'wb') as out:
        out.write(header)
        with __builtin__.open(name, 'rb') as infile:
            while True:
                decompData = infile.read((64*(1 << 10)))
                if not decompData:
                    break
                compData = lz4f.compressUpdate(decompData, cCtx)
                out.write(compData)
            out.write(lz4f.compressEnd(cCtx))
        out.flush()
        out.close()
    lz4f.freeCompContext(cCtx)


def compressTarDefault(name, overwrite=None, outname=None, prefs=None):
    """
    :type string: dirName   - the name of the dir to tar
    :type bool:   overwrite - overwrite destination
    Generic compress method for creating .tar.lz4 from a dir.

    ***WARNING*** Currently uses StringIO object until lz4file supports write.
    Avoid using for large directories, it will consume quite a bit of RAM.
    """
    if not outname:
        outname = '.'.join([name.rstrip('/'), 'tar', 'lz4'])
    if not os.path.exists(name):
        print('Unable to locate the directory to compress.')
        return
    buff = StringIO()
    tarbuff = Lz4Tar.open(fileobj=buff, mode='w')
    tarbuff.add(name)
    tarbuff.close()
    buff.seek(0)
    cCtx = lz4f.createCompContext()
    header = lz4f.compressBegin(cCtx, prefs)
    with __builtin__.open(outname, 'wb') as out:
        out.write(header)
        while True:
            decompData = buff.read((64*(1 << 10)))
            if not decompData:
                break
            compData = lz4f.compressUpdate(decompData, cCtx)
            out.write(compData)
        out.write(lz4f.compressEnd(cCtx))
        out.flush()
    lz4f.freeCompContext(cCtx)
    del tarbuff, buff


def decompressFileDefault(name, overwrite=False, outname=None):
    """
    :type string: name      - name of file to decompress
    :type bool:   overwrite - overwrite destination
    :type string: outname   - name for decompressed file, not required.
                              Default will be '.'.join([name, 'lz4'])
    Generic decompress method for a file. Removes .lz4 to original file name
    for output, unless outname is provided.

    ***WARNING*** Currently uses lz4f.compressFrame, which will read the entire
    original file into memory, then pass to c-module for compression. Avoid
    using this for large files until migrated to advCompress functions.
    """
    if not outname:
        outname = name.replace('.lz4', '')
        if outname == name:
            print(''.join(['File does not contain .lz4 extension. ',
                           'Please provide outname.']))
            return
        if os.path.exists(outname) and not overwrite:
            print(''.join(['Output file exists! Please authorize overwrite or',
                           ' specify a different outfile name.']))
    infile = Lz4File.open(name)
    infile.decompress(outname)


def getFileInfo(name):
    """
    :type string: name - name of file to examine
    Returns a dict object containing the file's header information.
    """
    if not os.path.exists(name):
        print('Unable to locate the file')
        return
    dCtx = lz4f.createDecompContext()
    with __builtin__.open(name, 'rb') as inFile:
        header = inFile.read(7)
    return lz4f.getFrameInfo(header, dCtx)


def open(name=None, fileObj=None):
    """  Alias for Lz4File.open()    """
    return Lz4File.open(name, fileObj)


def openTar(name=None, fileObj=None):
    """  Alias for Lz4Tar.open()     """
    return Lz4Tar.lz4open(name, 'r', fileObj)
