# -*- coding: utf-8 -*-

def f():
    print 'call f()....'
    #定义函数
    def g():
        print 'call g()....'
    #返回函数g:
    return g

x = f()
print x # 返回函数，<function g at 0x0000000002FB8048>


def calc_prod(lst):
    def fn(x, y):
        return x * y
    #  延迟计算，只有在calc_prod被调用时返回的函数被调用的时候，才会被计算
    def lazy_calc():
        return reduce(fn, lst)
        
    return lazy_calc

f = calc_prod([1, 2, 3, 4])
print f  # 返回的是函数<function lazy_calc at 0x0000000002FB8198>
print f() # 返回真正的计算值 24
