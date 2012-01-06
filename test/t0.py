# -*- Mode: Python -*-

import lljit

asm = """
define i32 @factorial(i32 %X) nounwind ssp {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  store i32 %X, i32* %2, align 4
  %3 = load i32* %2, align 4
  %4 = icmp eq i32 %3, 0
  br i1 %4, label %5, label %6

; <label>:5                                       ; preds = %0
  store i32 1, i32* %1
  br label %12

; <label>:6                                       ; preds = %0
  %7 = load i32* %2, align 4
  %8 = load i32* %2, align 4
  %9 = sub nsw i32 %8, 1
  %10 = call i32 @factorial(i32 %9)
  %11 = mul nsw i32 %7, %10
  store i32 %11, i32* %1
  br label %12

; <label>:12                                      ; preds = %6, %5
  %13 = load i32* %1
  ret i32 %13
}"""

m = lljit.module (asm, 0)
f = m.function ('factorial')

print f(3)
print f(5)
print f(10)
