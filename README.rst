
LLJIT
=====

This is a minimal interface to the JIT capability of LLVM_, exposed
via a Cython_ module.  It allows you to load either LLVM assembly code
or LLVM 'bitcode' and execute it via LLVM's ExecutionEngine. (i.e., JIT).

Motivation
----------

A much more complete interface to llvm exists, called llvm-py.  However,
at the time of this writing (LLVM 3.0) the LLVM API has changed enough that
updating llvm-py is a non-trivial project.

Sample Usage
------------

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

.. _Cython: http://cython.org/
.. _LLVM: http://llvm.org/
