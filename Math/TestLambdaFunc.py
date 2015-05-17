# -*- coding: cp936 -*-

# 这个例子用来测试lambda函数的使用

# 求平方
print map(lambda x: x * x, [1, 2, 3, 4, 5, 6, 7, 8, 9])  #[1, 4, 9, 16, 25, 36, 49, 64, 81]
# 排序，倒序
print sorted([1, 3, 9, 5, 0], lambda x,y: -cmp(x,y)) #[9, 5, 3, 1, 0]

# 求绝对值
myabs = lambda x: -x if x < 0 else x
print myabs(-1) # 1

# 去掉空和None
ls = ['test', None, '', 'str', 'END']
print filter(lambda x: x and len(x.strip()), ls)
