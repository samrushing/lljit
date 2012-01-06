# -*- Mode: Python -*-

# unencrypt an LLVM 'Bitcode' file.

import struct
import sys

W = sys.stderr.write

masks = [0] + [ (2<<n)-1 for n in range (32) ]

LLVM_IR_BLOCKS = {
    0 : 'BLOCKINFO',		# Standard block; contains metadata.
                                # ... 1-7 reserved for other standard blocks
    8 : 'MODULE_BLOCK',         # This is the top-level block that contains the entire module, and describes a variety of per-module information.
    9 : 'PARAMATTR_BLOCK',      # This enumerates the parameter attributes.
    10 : 'TYPE_BLOCK',          # This describes all of the types in the module.
    11 : 'CONSTANTS_BLOCK',     # This describes constants for a module or function.
    12 : 'FUNCTION_BLOCK',      # This describes a function body.
    13 : 'TYPE_SYMTAB_BLOCK',   # This describes the type symbol table.
    14 : 'VALUE_SYMTAB_BLOCK',  # This describes a value symbol table.
    15 : 'METADATA_BLOCK',      # This describes metadata items.
    16 : 'METADATA_ATTACHMENT', # This contains records associating metadata with function instruction values.
    }

def dec_string (val):
    return ''.join ([chr(x) for x in val])

dec_globalvar = None
dec_function  = None
dec_alias = None

MODULE_BLOCK = {
    1 : ('VERSION'     , None),
    2 : ('TRIPLE'      , dec_string),
    3 : ('DATALAYOUT'  , dec_string),
    4 : ('ASM'         , dec_string),
    5 : ('SECTIONNAME' , dec_string),
    6 : ('DEPLIB'      , dec_string),
    7 : ('GLOBALVAR'   , dec_globalvar),
    8 : ('FUNCTION'    , dec_function),
    9 : ('ALIAS'       , dec_alias),
    10 : ('PURGEVALS'  , None),
    11 : ('GCNAME'     , dec_string),
    }

TYPE_BLOCK = {
    1 : ('NUMENTRY', None),
    2 : ('VOID', None),
    3 : ('FLOAT', None),
    4 : ('DOUBLE', None),
    5 : ('LABEL', None),
    6 : ('OPAQUE', None),
    7 : ('INTEGER', None),
    8 : ('POINTER', None),
    9 : ('FUNCTION', None),
    10 : ('STRUCT', None),
    11 : ('ARRAY', None),
    12 : ('VECTOR', None),
    13 : ('X86_FP80', None),
    14 : ('FP128', None),
    15 : ('PPC_FP128', None),
    16 : ('METADATA', None),
    }

BLOCKINFO_BLOCK = {
    1 : ('SETBID', None),
    2 : ('BLOCKNAME', None),
    3 : ('SETRECORDNAME', None),
    }

TYPE_SYMTAB_BLOCK = {
    1 : 'ENTRY',
    }

# from llvm/Bitcode/LLVMBitCodes.h

FUNCTION_BLOCK = {
    1  : ('declareblocks', None),     # DECLAREBLOCKS: [n]
    2  : ('inst_binop', None),        # BINOP:      [opcode, ty, opval, opval]
    3  : ('inst_cast', None),         # CAST:       [opcode, ty, opty, opval]
    4  : ('inst_gep', None),          # GEP:        [n x operands]
    5  : ('inst_select', None),       # SELECT:     [ty, opval, opval, opval]
    6  : ('inst_extractelt', None),   # EXTRACTELT: [opty, opval, opval]
    7  : ('inst_insertelt', None),    # INSERTELT:  [ty, opval, opval, opval]
    8  : ('inst_shufflevec', None),   # SHUFFLEVEC: [ty, opval, opval, opval]
    9  : ('inst_cmp', None),          # CMP:        [opty, opval, opval, pred]
    10 : ('inst_ret', None),          # RET:        [opty,opval<both optional>]
    11 : ('inst_br', None),           # BR:         [bb#, bb#, cond] or [bb#]
    12 : ('inst_switch', None),       # SWITCH:     [opty, op0, op1, ...]
    13 : ('inst_invoke', None),       # INVOKE:     [attr, fnty, op0,op1, ...]
    14 : ('inst_unwind', None),       # UNWIND
    15 : ('inst_unreachable', None),  # UNREACHABLE
    16 : ('inst_phi', None),          # PHI:        [ty, val0,bb0, ...]
                                      # 17 is unused.
                                      # 18 is unused.
    19 : ('inst_alloca', None),       # ALLOCA:     [instty, op, align]
    20 : ('inst_load', None),         # LOAD:       [opty, op, align, vol]
                                      # 21 is unused.
                                      # 22 is unused.
    23 : ('inst_vaarg', None),        # VAARG:      [valistty, valist, instty]
                                      # This store code encodes the pointer type, rather than the value type
                                      # this is so information only available in the pointer type (e.g. address
                                      # spaces) is retained.
    24 : ('inst_store', None),        # STORE:      [ptrty,ptr,val, align, vol]
                                      # 25 is unused.
    26 : ('inst_extractval', None),   # EXTRACTVAL: [n x operands]
    27 : ('inst_insertval', None),    # INSERTVAL:  [n x operands]
                                      # fcmp/icmp returning Int1TY or vector of Int1Ty. Same as CMP, exists to
                                      # support legacy vicmp/vfcmp instructions.
    28 : ('inst_cmp2', None),         # CMP2:       [opty, opval, opval, pred]
                                      # new select on i1 or [N x i1]
    29 : ('inst_vselect', None),      # VSELECT:    [ty,opval,opval,predty,pred]
    30 : ('inst_inbounds_gep', None), # INBOUNDS_GEP: [n x operands]
    31 : ('inst_indirectbr', None),   # INDIRECTBR: [opty, op0, op1, ...]
                                      # 32 is unused.
    33 : ('debug_loc_again', None),   # DEBUG_LOC_AGAIN
    34 : ('inst_call', None),         # CALL:       [attr, fnty, fnid, args...]
    35 : ('debug_loc', None),         # DEBUG_LOC:  [Line,Col,ScopeVal, IAVal]
    36 : ('inst_fence', None),        # FENCE: [ordering, synchscope]
    37 : ('inst_cmpxchg', None),      # CMPXCHG: [ptrty,ptr,cmp,new, align, vol,
                                      #           ordering, synchscope]
    38 : ('inst_atomicrmw', None),    # ATOMICRMW: [ptrty,ptr,val, operation,
                                      #             align, vol,
                                      #             ordering, synchscope]
    39 : ('inst_resume', None),       # RESUME:     [opval]
    40 : ('inst_landingpad', None),   # LANDINGPAD: [ty,val,val,num,id0,val0...]
    41 : ('inst_loadatomic', None),   # LOAD: [opty, op, align, vol,
                                      #        ordering, synchscope]
    42 : ('inst_storeatomic', None),  # STORE: [ptrty,ptr,val, align, vol
                                      #         ordering, synchscope]
    }

block_names = {
    0 : BLOCKINFO_BLOCK,
    8 : MODULE_BLOCK,
    10 : TYPE_BLOCK,
    12 : FUNCTION_BLOCK,
    13 : TYPE_SYMTAB_BLOCK,
    }

char6 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._'

class bitcode:

    def __init__ (self, file):
        self.file = file
        self.bits = 0
        self.left = 0
        self.pos = 0
        # list, indexed by block code
        self.abbrevs = {}

    def read_x (self, n):
        # it's literally a bitstream - forget all about 'bytes'.
        # think of the file looking like this: [aabbccddeeffgg...]
        # when we ask for 6 bits we get: ccbbaa
        # then we ask for 8 bits and get: ggffeedd
        r = 0
        n0 = n
        while n > 0:
            if self.left == 0:
                self.bits, = struct.unpack ('<L', self.file.read (4))
                self.left = 32
                self.pos += 4
            shift = n0 - n
            if n > self.left:
                r |= self.bits << shift
                n -= self.left
                self.left = 0
                self.bits = 0
            else:
                r |= (self.bits & masks[n]) << shift
                self.left -= n
                self.bits >>= n
                n = 0
        return r

    def read (self, n):
        result = self.read_x (n)
        W ('read\t%d\t%d\n' % (n, result))
        return result

    def align (self):
        # align to 32 bits by tossing any remaining bits
        self.bits = 0
        self.left = 0
        W ('align (%d tossed)\n' % self.left)

    def read_vbr (self, n):
        r = 0
        shift = 0
        while 1:
            v = self.read (n)
            r |= (v & masks[n-1]) << shift
            if v & (1<<(n-1)):
                shift += n-1
            else:
                break
        return r

    def go (self):
        # read the wrapper first
        # http://llvm.org/docs/BitCodeFormat.html#wrapper
        # [I think it's a hack to make BC files palatable to Darwin]
        R = self.read
        magic32 = R(32)
        if magic32 == 0xb17c0de:
            self.version = R(32)
            self.offset  = R(32)
            self.size    = R(32)
            self.cputype = R(32)
        else:
            self.file.seek (0)
            self.align()
        assert (R(8), R(8)) == (0x42, 0x43) # 'BC'
        assert (R(4), R(4), R(4), R(4)) == (0x0, 0xc, 0xe, 0xd) # 'c0de'
        # ready to start reading blocks...
        self.codesize = [2]
        # only one block at the top level...
        return self.read_block (-1, 'top')
                
    def read_block_contents (self, bid, bname):
        result = []
        while 1:
            thing = self.read_block (bid, bname)
            if thing[0] == 'end_block':
                return result
            else:
                result.append (thing)

    def read_block (self, bid, bname):
        R = self.read
        code = R (self.codesize[-1])
        W ('read_block, code=%d\n' % code)
        result = []
        if code == 1: # ENTER_SUBBLOCK
            blockid = self.read_vbr (8)
            name = LLVM_IR_BLOCKS.get (blockid, blockid)
            W ('ENTER_SUBBLOCK %r\n' % (name,))
            self.codesize.append (self.read_vbr (4))
            self.align()
            block_len = R(32)
            W ('block_len %d\n' % block_len)
            return ('subblock', name, self.read_block_contents(blockid, name))
        elif code == 0: # END_BLOCK
            W ('END_BLOCK\n')
            self.codesize.pop()
            self.align()
            return ('end_block',)
        elif code == 2: # DEFINE_ABBREV
            num_ops = self.read_vbr (5)
            ops = []
            while num_ops:
                if self.read (1):
                    # literal
                    ops.append (('literal', self.read_vbr (8)))
                else:
                    encoding = self.read (3)
                    if encoding == 1:
                        ops.append (('fixed', self.read_vbr (5)))
                    elif encoding == 2:
                        ops.append (('vbr', self.read_vbr (5)))
                    elif encoding == 3:
                        ops.append (('array', None))
                    elif encoding == 4:
                        ops.append (('char6', None))
                    elif encoding == 5:
                        ops.append (('blob', None))
                num_ops -= 1
            if bname == 'BLOCKINFO':
                self.add_abbrev (self.bi_setbid, ops)
            else:
                self.add_abbrev (bid, ops)
            W ('DEFINE_ABBREV %r\n' % (ops,))
            return ('define_abbrev', ops)
        elif code == 3: # UNABBREV_RECORD
            record_code = self.read_vbr (6)
            num_ops = self.read_vbr (6)
            ops = []
            while num_ops:
                ops.append (self.read_vbr (6))
                num_ops -= 1
            if bname == 'BLOCKINFO':
                if record_code == 1:
                    self.bi_setbid = ops[0]
                    W ('  SETBID %d\n' % (self.bi_setbid,))
                elif record_code == 2:
                    import pdb; pdb.set_trace()
            record_code, value = self.decode_record (bid, record_code, ops)
            W ('UNABBREV_RECORD: code=%r rcode=%r value=%r\n' % (code, record_code, value))
            return ('record', record_code, value)
        else:
            return self.decode_abbrev (bid, code)
                
    def decode_record (self, bid, code, value):
        probe = block_names.get (bid, None)
        if probe:
            probe = probe.get (code, None)
            if probe:
                name, decoder = probe
                if decoder:
                    value = decoder (value)
                return name, value
        return code, value

    def read_abbrev (self, entries):
        kind, param = entries.pop(0)
        W ('reading abbrev %r, %r\n' % (kind, param))
        if kind == 'literal':
            return param
        elif kind == 'fixed':
            return self.read (param)
        elif kind == 'vbr':
            return self.read_vbr (param)
        elif kind == 'array':
            result = []
            akind, aparam = entries.pop(0)
            length = self.read_vbr (6)
            W ('  array[%d] of %r, %r\n' % (length, akind, aparam))
            for i in range (length):
                result.append (self.read_abbrev ([(akind,aparam)]))
            if akind == 'char6':
                # hack
                result = ''.join (result)
            return result
        elif kind == 'char6':
            return char6[self.read(6)]
        else:
            raise NotImplementedError

    def add_abbrev (self, bid, entry):
        if not self.abbrevs.has_key (bid):
            self.abbrevs[bid] = []
        self.abbrevs[bid].append (entry)

    def decode_abbrev (self, bid, code):
        abbrevs = self.abbrevs[bid]
        entry = abbrevs[code-4][:]
        W ('decoding abbrev: %r\n' % (entry,))
        i = 0
        result = []
        while entry:
            result.append (self.read_abbrev (entry))
        code, value = self.decode_record (bid, code, result)
        return ('abbrev', code, value)

if __name__ == '__main__':
    import sys
    from pprint import pprint as pp
    bs = bitcode (open (sys.argv[1], 'rb'))
    all = bs.go()
    pp (all)
