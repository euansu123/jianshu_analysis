

# dic1 = {
#     'noteid':33,
#     'time': '2020-09-11 15:37:47',
#     'name':'euansu'
# }
#
# dic2 = {
#     'noteid':34,
#     'time': '2020-09-12 15:37:47'
# }
#
# dic3 = dict(dic1,**dic2)
# print(dic3)

# dic3 = {
#     'noteid':35,
#     'time': '2020-09-08 15:37:47'
# }
#
# diclis = []
# diclis.append(dic1)
# diclis.append(dic2)
# diclis.append(dic3)
#
# print(diclis)

# def sortdic(dic):
#     return dic['time']

# sorted_lst = sorted(diclis,key=sortdic) # sorted():按照字典的某一个key值进行排序
# print(sorted_lst)
#
# sorted_lst = sorted(diclis,key=lambda dic:dic['time']) # sorted():按照字典的某一个key值进行排序
# print(sorted_lst)

# def extract_first_time(lst):
#     sorted_lst = sorted(diclis,key=lambda dic:dic['time'])
#     return sorted_lst[0]
#
# r = extract_first_time(diclis)
# print(r)
# 统计月份
from collections import Counter

import jieba

lst = ['2020-09','2020-08','2020-07','2020-10','2020-09']
# counter = Counter(lst)
# print(counter.items())
# sorted_counter = sorted(counter.items(),key=lambda tup:tup[0])
# print(sorted_counter)

# def sorted_month(lst):
#     counter = Counter(lst)
#     sorted_counter = sorted(counter.items(), key=lambda tup: tup[0])
#     dic_month_data = {
#         'month_line':[t[0] for t in sorted_counter],
#         'month_freqency':[t[1] for t in sorted_counter]
#     }
#     return dic_month_data
#
# r = sorted_month(lst)
# print(r)

# newlst = ['2020-09','2020-08','2020-07','2020-10','2020-09','2020-10','2020-10']
# counter = Counter(newlst)
# print(counter.items()) # 可以计算次数
# # 想要获得最多的次数
# counter_sorted = sorted(counter.items(),key=lambda t:t[0]) # 按照时间排序
# print(counter_sorted)
#
# t = counter.most_common(1)[0][1] # 出现次数最多的次数
# print(t)

# 分词
words = "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。Python 由 Guido van Rossum 于 1989 年底发明，第一个公开发行版发行于 1991 年。像 Perl 语言一样, Python 源代码同样遵循 GPL(GNU General Public License) 协议。官方宣布，2020 年 1 月 1 日， 停止 Python 2 的更新。Python 2.7 被确定为最后一个 Python 2.x 版本"

wordlst = jieba.cut(words)
print(list(wordlst))