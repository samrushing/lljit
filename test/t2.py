# -*- Mode: Python -*-

# playing around with tagged integers here.
# in Irken I set the lowest bit to indicate an 'integer', trying to
#   see if I can model that directly in llvm.
#
# note: doesn't seem to work the way I want, either 'packed' or not.

import lljit

asm = """
%int_t = type <{ i63, i1 }>

@con0 = global %int_t <{ i63 3141, i1 1 }>

define %int_t @tagadd(%int_t %a, %int_t %b) {
  %av = extractvalue %int_t %a, 0
  %bv = extractvalue %int_t %b, 0
  %sv = add i63 %av, %bv
  %agg1 = insertvalue %int_t undef, i63 %sv, 0
  %agg2 = insertvalue %int_t %agg1, i1 1, 1
  ret %int_t %agg2
}

define %int_t @funn (%int_t %x) {
  %agg1 = insertvalue %int_t undef, i63 3141, 0
  %agg2 = insertvalue %int_t %agg1, i1 1, 1
  %r = call %int_t @tagadd (%int_t %agg2, %int_t %x)
  store %int_t %r, %int_t* @con0
  ret %int_t %r
} """

m = lljit.module (asm, 0)
f = m.function ('funn')
print f (100)
