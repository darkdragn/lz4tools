==================
Lz4tools and Lz4f
==================

.. image:: https://travis-ci.org/darkdragn/lz4tools.svg?branch=modular

Overview
--------
This package consists of two parts:

1. lz4f - C-Module containing python bindings for all lz4frame functions.
2. lz4tools - a zipfile-like file wrapper class and tarfile-like class for lz4 compressed files. 
3. lz4toolsCli - a quick cli for using lz4tools static functions.

Before going any further, I recommend reading up on lz4 at: https://code.google.com/p/lz4/

It is an awesome compression algorithm and I can't thank Yann Collet enough for putting together the C implementation and lz4frame.

Usage
-----
Cli:
    New addition, there is now a simple Cli for anyone wishing these capabilities would exist directly on the command line.
    
::

    usage: lz4toolsCli [-h] [-f] [-t] [-d] [-i] [-bs {4,5,6,7}] [-bm {0,1}]
                       input [output]
    
    positional arguments:
      input          The targeted input.
      output         Optional output target.
    
    optional arguments:
      -h, --help     show this help message and exit
      -f             Compress file. Default action if input is a file.
      -t             Compress directory to .tar.lz4. Default action if input is a
                     directory
      -d             Decompress file. Default action if the file ends in .lz4.
      -i             Print frame information from the file's header.
      -bs {4,5,6,7}  Specify blkSizeId. Valid values are 4-7. Default value is 7.
      -bm {0,1}      Specify blkMode. 0 = Chained blocks. 1 = Independent blocks
                     Default value is 0.

..

C-Module / Bindings:
    I would recommend against using lz4f directly except in debug/testing situations. If necessary, a compress or decompress operation first needs a context that will be used with all lz4f functions:

    lz4f compression the hard way:
        >>> import lz4f
        >>> inputFile = open('fileIn', 'rb')
        >>> cCtx = lz4f.createCompressionContext
        >>> header = lz4f.compressBegin(cCtx)
        >>> data = lz4f.compressUpdate(inputFile.read(), cCtx)
        >>> end = lz4f.compressEnd(cCtx)
        >>> with open('output.lz4', 'wb') as out:
        ...     out.write(header)
        ...     out.write(data)
        ...     out.write(end)
        ...     out.flush()
        ...     out.close()
        >>> lz4f.freeCompContext(cCtx)
        >>> inputFile.close()
        >>> del header, data, end
    
    lz4f compression the easy way:
        >>> import lz4f
        >>> with open('output.lz4', 'wb') as out:
        ...     with open('fileIn', 'rb') as inFile:
        ...         out.write(lz4f.compressFrame(inFile.read())
        ...     out.flush()
        ...     out.close()
    
    Advantages and disadvantages: The easy way takes more ram. It reads the contents of the file into a buffer, passes it and compresses it all in one go. With the hard way you can have it read as little or as much as you like. For instance, you can break up the input into 64k chunks. Each chunk could be read, compressed and dropped to disk to conserve ram.

..

Lz4Tools Module:
    The lz4file class is currently read only. Right now it is a bit rough around the edges, however over the next couple of weeks, I will finish adding some document strings, and such to make it more user friendly. As soon as I get a chance I will make it write capable. The easiest way to use it is with either the open or openTar methods. That's right! There is a lz4Tar class in the module that is a subclass of tarfile. 

    lz4tools tar example:
        >>> import lz4tools
        >>> lz4tools.compressTarDefault('src')
        >>> testTar = lz4tools.openTar('src.tar.lz4')
        >>> testTar.list()
        -rwxr-xr-x darkdragn/darkdragn          0 2014-10-02 23:06:09 src/
        -rw-r--r-- darkdragn/darkdragn      29905 2014-09-16 18:29:45 src/lz4hc.c
        -rw-r--r-- darkdragn/darkdragn       6781 2014-09-16 18:29:45 src/  xxhash.h
        -rw-r--r-- darkdragn/darkdragn      25662 2014-09-16 18:29:45 src/  xxhash.c
        -rw-rw-r-- darkdragn/darkdragn      13894 2014-10-02 20:22:09 src/lz4frame.h
        -rw-rw-r-- darkdragn/darkdragn      46241 2014-10-02 20:22:09 src/lz4.c
        -rw-r--r-- darkdragn/darkdragn       8832 2014-09-16 18:29:45 src/lz4hc.h
        -rw-rw-r-- darkdragn/darkdragn      11734 2014-10-02 23:06:08 src/python-lz4f.c
        -rw-rw-r-- darkdragn/darkdragn       2554 2014-10-02 20:22:09 src/python-lz4f.h
        -rw-r--r-- darkdragn/darkdragn      14882 2014-09-18 01:28:06 src/lz4.h
        -rw-rw-r-- darkdragn/darkdragn      50141 2014-10-02 23:04:05 src/lz4frame.c
    
    lz4tools file example:
        >>> import lz4tools
        >>> lz4tools.compressFileDefault('setup.py')
        >>> testFile = lz4tools.open('setup.py.lz4')
        >>> testFile.blkDict
        {0: {'decomp_e': 1445, 'compressed_begin': 7, 'blkSize': 923}}
        >>> testFile.seek(1002)
        >>> print testFile.read()
            test_suite = "nose.collector",
            keywords = ['lz4', 'lz4frame', 'lz4file', 'lz4tar'],
            classifiers=[
                'Development Status :: 5 - Production/Stable',
                'License :: OSI Approved :: BSD License',
                'Intended Audience :: Developers',
                'Programming Language :: C',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
            ],
        )

And thus ends the brief tutoral.

Notes
-----

Version : 
    The first two digits of the version will always correspond with the version of lz4 that is included. Current version is r124, thus 1.2. The next  digit is correspond to milestone improvements. Example: Once lz4file supports write. The last digit will be slight improvements. Usually some contextual error, or syntax error. Perhaps even a quick fix for python3.4, since I don't use it often, if an issue is brought to my attention, I will provide a quick fix as quickly as possible. 
