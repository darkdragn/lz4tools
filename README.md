LZ4tools and LZ4f
================


Overview
--------
This package consists of two parts:

1. lz4f - bindings for all lz4frame functions

2. lz4tools - a zipfile-like file wrapper and tarfile-like class for lz4 compressed files. 

Usage
-----
I would recommend against using lz4f directly except in debug/testing situations. If necessary, a compress or decompress operation first needs a context that will be used with all lz4f functions:

    lz4f compression the hard way:
    >>> import lz4f
    >>> inputFile = open('fileIn')
    >>> cCtx = lz4f.createCompressionContext
    >>> header = lz4f.compressBegin(cCtx)
    >>> data = lz4f.compressUpdate(inputFile.read(), cCtx)
    >>> end = lz4f.compressEnd(cCtx)
    >>> with open('output.lz4', 'w') as out:
    ...     out.write(header)
    ...     out.write(data)
    ...     out.write(end)
    ...     out.flush()
    ...     out.close()
    
    lz4f compression the easy way:
    >>> import lz4f
    >>> with open('output.lz4') as out:
    ...     with open('fileIn') as inFile:
    ...         out.write(lz4f.compressFrame(inFile.read())
    ...     out.flush()
    ...     out.close()
    
Advantages and disadvntages: The easy way takes more ram. It reads the contents of the file into a buffer, passes it and compresses it all in one go. With the hard way you can have it read as little or as much as you like. For instance, you can break up the input into 64k chunks. Each chunk could be read, compressed and dropped to disk to conserve ram.

The lz4file module is currently read only. Right now it is a bit rough around the edges, however over the next couple of weeks, I will finish adding some document strings, and such to make it more user friendly. As soon as I get a chance I will make it write capable. The easiest way to use it is with either the open or openTar methods. That's right! There is a lz4Tar class in the module that is a subclass of tarfile. 

    lz4file tar example:
    >>> import lz4tools
    >>> lz4tools.compressTarDefault('src')
    >>> testTar = lz4tools.openTar('src.lz4')
    >>> testTar.list()
    -rwxr-xr-x darkdragn/darkdragn          0 2014-10-02 23:06:09 src/
    -rw-r--r-- darkdragn/darkdragn      29905 2014-09-16 18:29:45 src/lz4hc.c
    -rw-r--r-- darkdragn/darkdragn       6781 2014-09-16 18:29:45 src/xxhash.h
    -rw-r--r-- darkdragn/darkdragn      25662 2014-09-16 18:29:45 src/xxhash.c
    -rw-rw-r-- darkdragn/darkdragn      13894 2014-10-02 20:22:09 src/lz4frame.h
    -rw-rw-r-- darkdragn/darkdragn      46241 2014-10-02 20:22:09 src/lz4.c
    -rw-r--r-- darkdragn/darkdragn       8832 2014-09-16 18:29:45 src/lz4hc.h
    -rw-rw-r-- darkdragn/darkdragn      11734 2014-10-02 23:06:08 src/python-lz4f.c
    -rw-rw-r-- darkdragn/darkdragn       2554 2014-10-02 20:22:09 src/python-lz4f.h
    -rw-r--r-- darkdragn/darkdragn      14882 2014-09-18 01:28:06 src/lz4.h
    -rw-rw-r-- darkdragn/darkdragn      50141 2014-10-02 23:04:05 src/lz4frame.c
    
    lz4file file example:
    >>> import lz4tools
    >>> lz4tools.compressFileDefault('setup.py')
    >>> testFile = lz4tools.open('setup.py.lz4')
    >>> print testFile.blkDict
        {0: {'decomp_e': 6584, 'compressed_begin': 7, 'blkSize': 3109}}
    >>> testFile.end
        6583
    >>> testFile.pos
        0   
    >>> testFile.seek(6293)
    >>> print testFile.read()
        def open(name=None, fileObj=None):
            return Lz4File.open(name, fileObj)
        def openTar(name=None, fileObj=None):
            return Lz4Tar.lz4open(name, 'r', fileObj)
        def tell_end(fileObj):
            pos = fileObj.tell()
            fileObj.seek(0, 2)
            end = fileObj.tell()
            fileObj.seek(pos)
            return end
And thus ends the brief tutoral.


