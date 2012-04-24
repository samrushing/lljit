# -*- Mode: Cython -*-

from libcpp.string cimport string

# --------------------------------------------------------------------------------
# minimal declarations to get to the LLVM JIT API.
# --------------------------------------------------------------------------------

cdef extern from "llvm/LLVMContext.h" namespace "llvm":
    cdef cppclass LLVMContext:
        pass

cdef extern from "llvm/Support/SourceMgr.h" namespace "llvm":
    cdef cppclass SMDiagnostic:
        int getLineNo()
        int getColumnNo()
        string getFilename()
        string getMessage()

# Note: if LLVM < 3, I think this needs to be "llvm/Target/TargetSelect.h"
cdef extern from "llvm/Support/TargetSelect.h" namespace "llvm":
    cdef bint InitializeNativeTarget()

cdef extern from "llvm/Module.h" namespace "llvm":
    cdef cppclass Module:
        void dump()

cdef extern from "llvm/Support/MemoryBuffer.h" namespace "llvm":
    cdef cppclass MemoryBuffer:
        char * getBufferStart()
        size_t getBufferSize()
    # note naming hack to get to the static method (also note that we lose the
    #   namespace in the override).
    cdef MemoryBuffer * MemoryBuffer_getMemBuffer "llvm::MemoryBuffer::getMemBuffer" (string)

cdef extern from "llvm/Support/DynamicLibrary.h" namespace "llvm":
    cdef bint DynamicLibrary_LoadLibraryPermanently "llvm::sys::DynamicLibrary::LoadLibraryPermanently" (char * name, string * ErrMsg)

cdef extern from "llvm/Bitcode/ReaderWriter.h" namespace "llvm":
    cdef Module * ParseBitcodeFile (MemoryBuffer * Buffer, LLVMContext Context, string * ErrMsg)

cdef extern from "llvm/Assembly/Parser.h" namespace "llvm":
    cdef Module * ParseAssembly (
        MemoryBuffer * F,       # The MemoryBuffer containing assembly
        Module * M,             # A module to add the assembly too.
        SMDiagnostic Err,       # Error result info.
        LLVMContext Context
        )

cdef extern from "llvm/Pass.h" namespace "llvm":
    cdef cppclass Pass:
        pass
    cdef cppclass ImmutablePass (Pass):
        pass
    cdef cppclass FunctionPass (Pass):
        pass

cdef extern from "llvm/Transforms/Scalar.h" namespace "llvm":
    Pass * createConstantPropagationPass()
    Pass * createSCCPPass()
    Pass * createDeadInstEliminationPass()
    Pass * createDeadCodeEliminationPass()
    Pass * createDeadStoreEliminationPass()
    Pass * createAggressiveDCEPass()
    Pass * createScalarReplAggregatesPass()
    Pass * createIndVarSimplifyPass()
    Pass * createInstructionCombiningPass()
    Pass * createLICMPass()
    Pass * createLoopStrengthReducePass()
    Pass * createGlobalMergePass()
    Pass * createLoopUnswitchPass()
    Pass * createLoopInstSimplifyPass()
    Pass * createLoopUnrollPass()
    Pass * createLoopRotatePass()
    Pass * createLoopIdiomPass()
    Pass * createPromoteMemoryToRegisterPass()
    Pass * createDemoteRegisterToMemoryPass()
    Pass * createReassociatePass()
    Pass * createJumpThreadingPass()
    Pass * createCFGSimplificationPass()
    Pass * createBreakCriticalEdgesPass()
    Pass * createLoopSimplifyPass()
    Pass * createTailCallEliminationPass()
    Pass * createLowerSwitchPass()
    Pass * createLowerInvokePass()
    Pass * createBlockPlacementPass()
    Pass * createLCSSAPass()
    Pass * createEarlyCSEPass()
    Pass * createGVNPass()
    Pass * createMemCpyOptPass()
    Pass * createLoopDeletionPass()
    Pass * createSimplifyLibCallsPass()
    Pass * createCodeGenPreparePass()
    Pass * createInstructionNamerPass()
    Pass * createSinkingPass()
    Pass * createLowerAtomicPass()
    Pass * createCorrelatedValuePropagationPass()
    Pass * createObjCARCExpandPass()
    Pass * createObjCARCContractPass()
    Pass * createObjCARCOptPass()
    Pass * createInstructionSimplifierPass()
    Pass * createLowerExpectIntrinsicPass()

cdef extern from "llvm/Analysis/Passes.h" namespace "llvm":
    Pass * createGlobalsModRefPass()
    Pass * createAliasDebugger()
    Pass * createAliasAnalysisCounterPass()
    Pass * createAAEvalPass()
    Pass * createNoAAPass()
    Pass * createBasicAliasAnalysisPass()
    Pass * createLibCallAliasAnalysisPass()
    Pass * createScalarEvolutionAliasAnalysisPass()
    Pass * createTypeBasedAliasAnalysisPass()
    Pass * createObjCARCAliasAnalysisPass()
    Pass * createProfileLoaderPass()
    Pass * createNoProfileInfoPass()
    Pass * createProfileEstimatorPass()
    Pass * createProfileVerifierPass()
    Pass * createNoPathProfileInfoPass()
    Pass * createPathProfileVerifierPass()
    Pass * createDSAAPass()
    Pass * createDSOptPass()
    Pass * createSteensgaardPass()
    Pass * createLazyValueInfoPass()
    Pass * createLoopDependenceAnalysisPass()
    Pass * createInstCountPass()
    Pass * createDbgInfoPrinterPass()
    Pass * createRegionInfoPass()
    Pass * createModuleDebugInfoPrinterPass()
    Pass * createMemDepPrinter()

cdef extern from "llvm/PassManager.h" namespace "llvm":
    cdef cppclass FunctionPassManager:
        FunctionPassManager (Module *)
        void add (Pass *)
        bint doInitialization()
        bint doFinalization()
        void run (Function)

cdef extern from "llvm/Function.h" namespace "llvm":
    cdef cppclass Function:
        pass

cdef extern from "llvm/ExecutionEngine/JIT.h" namespace "llvm":
    cdef cppclass ExecutionEngine:
        Function * FindFunctionNamed (char *FnName)
        void * getPointerToFunction (Function *)
    # static method
    cdef ExecutionEngine * ExecutionEngine_create "llvm::ExecutionEngine::create" (Module *)

