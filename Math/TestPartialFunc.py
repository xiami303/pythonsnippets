# -*- coding: cp936 -*-
# 这个例子是用来测试functools.partial的
import functools
# int方法的正常使用方法
int('12345')
int('12345', base=8)
int('12345', base=16)

def int2(x, base=2):
    return int(x, base)

print int2('1000000')
int2('1000000')  #64


'''
functools.partial就是帮助我们创建一个偏函数的，
不需要我们自己定义int2()，
可以直接使用下面的代码创建一个新的函数int2：
'''
int2 = functools.partial(int, base=2)
int2('1000000')  #64
'''
functools.partial可以把一个参数多的函数变成一个参数少的新函数，
少的参数需要在创建时指定默认值，这样，新函数调用的难度就降低了
'''


'''
在sorted这个高阶函数中传入自定义排序函数就可以实现忽略大小写排序。
下面用functools.partial把这个复杂调用变成一个简单的函数：
'''
def ignore_case(x, y):
    x = x.lower()
    y = y.lower()
    if x >y:
        return 1
    elif x<y:
        return -1
    return 0
    
#为cmp传递了自定义的cmp函数，ignore_case 为自定义的cmp函数
sorted_ignore_case = functools.partial(sorted, cmp= ignore_case)
#test
print sorted_ignore_case(['bob', 'about', 'Zoo', 'Credit']) #['about', 'bob', 'Credit', 'Zoo']
