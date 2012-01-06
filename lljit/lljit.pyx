# -*- Mode: Cython -*-
# distutils: language = c++

# Use LLVM's JIT engine to load up some LLVM IR (or bitcode) and execute it.

# lotsa clues from here:
# http://stackoverflow.com/questions/1838304/call-the-llvm-jit-from-c-program

from llvm cimport *

# global initialization
cdef bint init_nt = InitializeNativeTarget()
cdef LLVMContext * context = new LLVMContext()

class LLVMError (Exception):
    pass

ctypedef int iifun (int)

cdef class sm_diagnostic:
    cdef SMDiagnostic * d
    def __cinit__ (self):
        self.d = new SMDiagnostic()
    def __dealloc__ (self):
        del self.d
    def __repr__ (self):
        return '<diag file:%r line:%d col:%d %r>' % (
            self.d.getFilename().c_str(),
            self.d.getLineNo(),
            self.d.getColumnNo(),
            self.d.getMessage().c_str()
            )

cdef class memory_buffer:
    cdef MemoryBuffer * mb
    cdef string * data
    def __cinit__ (self, bytes s):
        self.data = new string (<char*>s, <size_t>len(s))
        self.mb = MemoryBuffer_getMemBuffer (self.data[0])
    def __dealloc__ (self):
        # segfault, who owns this?
        #del self.mb
        del self.data

cdef class module:
    cdef Module * module
    cdef ExecutionEngine * engine
    cdef FunctionPassManager * fpm

    def __init__ (self, bytes code, bint binary):
        # load the code into LLVM and JIT it.
        self.load_code (code, binary)

    def __dealloc__ (self):
        # segfault, who owns this?
        #del self.function
        del self.module
        #del self.engine

    cdef load_code (self, bytes code, bint binary):
        cdef sm_diagnostic diag = sm_diagnostic()
        cdef string * error = new string()
        cdef memory_buffer mb = memory_buffer (code)
        if binary:
            self.module = ParseBitcodeFile (mb.mb, context[0], error)
            if not self.module:
                raise LLVMError ("ParseBitcodeFile", error.c_str())
        else:
            self.module = ParseAssembly (mb.mb, NULL, diag.d[0], context[0])
            if not self.module:
                raise LLVMError ("ParseAssembly", repr(diag))
        self.engine = ExecutionEngine_create (self.module)
        if not self.engine:
            raise LLVMError ("ExecutionEngine::create")
        self.fpm = new FunctionPassManager (self.module)
        if not self.fpm:
            raise LLVMError ("FunctionPassManager")
        self.fpm.add (createBasicAliasAnalysisPass())
        self.fpm.add (createInstructionCombiningPass())
        self.fpm.add (createReassociatePass())
        self.fpm.add (createGVNPass())
        self.fpm.add (createCFGSimplificationPass())
        self.fpm.add (createPromoteMemoryToRegisterPass())
        self.fpm.add (createTailCallEliminationPass())
        self.fpm.doInitialization()

    def dump (self):
        self.module.dump()

    def function (self, name):
        return function (self, name)

cdef class function:
    cdef module mod
    cdef iifun * code_pointer
    cdef Function * function

    def __init__ (self, module mod, bytes name):
        self.mod = mod
        self.function = self.mod.engine.FindFunctionNamed (name)
        if not self.function:
            raise LLVMError ("FindFunctionNamed", name)
        self.mod.fpm[0].run (self.function[0])
        if self.function:
            self.code_pointer = <iifun*> self.mod.engine.getPointerToFunction (self.function)
        else:
            raise LLVMError ("FindFunctionNamed", name)

    def __call__ (self, int arg):
        if not self.code_pointer:
            raise LLVMError ("no code pointer!")
        return self.code_pointer (arg)
