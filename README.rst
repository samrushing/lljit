
LLJIT
=====

This is a minimal interface to the JIT capability of LLVM_, exposed
via a Cython_ module.  It allows you to load either LLVM assembly_ code
or LLVM bitcode_ and execute it via LLVM's ExecutionEngine. (i.e., JIT).

Motivation
----------

A much more complete interface to llvm exists, called llvm-py_.  However,
at the time of this writing (LLVM 3.0) the LLVM API has changed enough that
updating llvm-py is a non-trivial project.

Building
--------

You'll need LLVM 3.0+ to build.  It probably wouldn't be difficult to make
this work with an older LLVM but I haven't bothered to try.

You may need to change the path of an include file in lljit/llvm.pxd, see
the comments if you get this error:

  lljit/lljit.cpp:238:39: fatal error: llvm/Support/TargetSelect.h: No such file or directory

The LLVM API is a moving target!

Build/install:

  1. $ python setup.py build
  2. $ sudo python setup.py install

Sample Usage
------------

Lo,::

  import lljit
  
  # calling an external function...
  
  asm = """
  declare i32 @getpid()
  define i32 @thing (i32 %x) {
    %1 = sub nsw i32 %x, 1
    %2 = call i32 @getpid()
    %3 = add i32 %2, %1
    ret i32 %3
  }"""
  
  m = lljit.module (asm, 0)
  f = m.function ('thing')
  
  print f(3)
  print f(5)
  print f(10)

Bitcode
-------

I've included a module for parsing bitcode_ files.  There are still problems,
it is interpreting the insn sequences incorrectly, but the major difficulty
of parsing the bit stream correctly has been cracked.  I may eventually add
an ability to *write* bitcode (e.g., for the backend of a compiler).

LLVM Hints
----------

If you're new to LLVM, here are some quick hints to get you started.

Compile a C file to llvm assembly::

  $ clang -emit-llvm -S t.c
  [or]
  $ llvm-gcc -emit-llvm -S t.c

Optimize some llvm assembly:

  $ opt -std-compile-opts t.s -S

Compile to native code:

  $ cat t.s | opt -std-compile-opts | llc

Compile to a different architecture:

  $ cat t.s | opt -std-compile-opts | llc -march=arm


.. _Cython: http://cython.org/
.. _LLVM: http://llvm.org/
.. _bitcode: http://llvm.org/docs/BitCodeFormat.html
.. _assembly: http://llvm.org/docs/LangRef.html
.. _llvm-py: http://www.mdevan.org/llvm-py/

