# -*- Mode: Python -*-

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
