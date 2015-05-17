# -*- coding: cp936 -*-

# 闭包：在内层函数中引用了外层函数的变量（参数也算是变量），然后返回内层函数的情况，称为闭包
# 坑： 闭包由于引用了外部变量，但是要确保局部变量在函数返回后不能变，因此不能在内部函数中修改循环变量


# eg: 下面这个例子中，由于修改了循环变量i，导致最后调用f1, f2, f3的结果打印是9， 9， 9
def count():
    fs = []
    for i in range(1, 4):
        def f():
             return i*i
        fs.append(f)
    return fs

f1, f2, f3 = count()
print f1(), f2(), f3() # 9 9 9


def count2():
   fs = []
   for i in range(1, 4):
       def f(j):  ## 将循环变量作为参数传递给函数
           def g():
               return j*j
           return g
       fs.append(f(i))  # 返回带参数的函数
   return fs
f1, f2, f3 = count2()
print f1(), f2(), f3()  # 1 4 9
