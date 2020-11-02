import re
from collections import Counter
from datetime import datetime

import jieba
from flask import Flask, render_template, request, redirect
from pyecharts import WordCloud

from jianshu_flask.PandasAnlysisUserinfo import PandasAnlysisUserinfo
from jianshu_flask.config import *
from jianshu_flask.get_user_info import GetUserInfo
import pymongo
from jianshu_flask.config import *


app = Flask(__name__)

# 连接mongodb
client = pymongo.MongoClient(MONGO_HOST,MONGO_PORT)
# 选中要进行操作的数据库
db = client[MONGO_TABLE]

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        formdata = request.form['url']
        match_result = re.match('(https://www.jianshu.com/u/)?(\w{12}|\w{6})', formdata)
        user_slug = match_result.groups()[-1]
        # print(user_slug)
        # 数据库中查询
        userdata = db['user_timeline'].find_one({'slug':user_slug})
        if userdata != None:
            last_time = userdata['last_time'] # 上一次爬取内容的节点
        else:
            last_time = ''
        # 这里是抓取用户信息
        gui = GetUserInfo(user_slug)
        item = gui.get_user_info()
        # print(item)
        db['user_timeline'].update({'slug':item['slug']},{'$set':item},upsert=True)
        if userdata != None:
            gui.timeline = userdata
        gui.get_user_timeline(last_time)
        db['user_timeline'].update({'slug': item['slug']}, {'$set': gui.timeline}, upsert=True)
        time_line = gui.timeline

        item['like_notes_num'] = len(time_line['like_notes'])
        item['like_colls_num'] = len(time_line['like_colls'])
        item['like_nbs_num'] = len(time_line['like_notebooks'])
        item['comment_notes_num'] = len(time_line['comment_notes'])
        item['like_comments_num'] = len(time_line['like_comments'])
        item['reward_notes_num'] = len(time_line['reward_notes'])
        first_tag_time = get_first_tag_time(time_line)
        # print(first_tag_time)
        # 获取各项目的数据
        tags_data = gui.tags_data()
        # 获取时间线
        time_data = gui.get_tag_month_data()
        # 数据分析：普通分析——月份数据
        # month_data = [time[0:7] for time in time_data]
        # counter = Counter(month_data)
        # sorted_counter = sorted(counter.items(), key=lambda tup: tup[0])
        # dic_month_data = {
        #     'month_line': [t[0] for t in sorted_counter],
        #     'month_freqency': [t[1] for t in sorted_counter]
        # }

        # 数据分析：pandas分析——月份数据
        pau = PandasAnlysisUserinfo(user_slug)
        dic_month_data = pau.pd_get_month_data()

        # 天的数据
        # day_data = [time[0:10] for time in time_data]
        # counter = Counter(day_data)
        # sorted_counter = sorted(counter.items(), key=lambda tup: tup[0])
        # dic_day_data = {
        #     'day_line': [t[0] for t in sorted_counter],
        #     'day_freqency': [t[1] for t in sorted_counter]
        # }

        dic_day_data = pau.pd_get_day_data()

        # 小时数据
        # hour_data = [time[11:13] for time in time_data]
        # counter = Counter(hour_data)
        # sorted_counter = sorted(counter.items(), key=lambda tup: tup[0])
        # dic_hour_data = {
        #     'hour_line': [t[0] for t in sorted_counter],
        #     'hour_freqency': [t[1] for t in sorted_counter]
        # }

        dic_hour_data = pau.pd_get_hour_data()

        # week_data = [time_week(time) for time in time_data]
        # counter = Counter(week_data)
        # sorted_counter = sorted(counter.items(), key=lambda tup: tup[0])
        # dic_week_data = {
        #     'week_line': [t[0][1:] for t in sorted_counter],
        #     'week_freqency': [t[1] for t in sorted_counter]
        # }

        dic_week_data = pau.pd_get_week_data()

        # 周，小时数据
        # week_hour_data = []
        # for time in time_data:
        #     week_hour = time_week(time)[0] + time[11:13]
        #     week_hour_data.append(week_hour)
        # # print(week_hour_data)
        # counter = Counter(week_hour_data)
        # # 准备一个空列表。将元组变为列表
        # dic_week_hour_data = []
        # for data in counter.items():
        #     # print(data)
        #     # print(data[0][1])
        #     # ('218', 7)
        #     # 需要转化成[2.18,7]的形式
        #     each = [int(data[0][0]),int(data[0][1:]),int(data[1])]
        #     # print(each)
        #     dic_week_hour_data.append(each)
        # # print(dic_week_hour_data)
        #
        # # 获取最多的次数
        # max_freq = counter.most_common(1)[0][1]
        # print(max_freq)

        max_freq, dic_week_hour_data = pau.pd_get_week_hour_data()
        print(max_freq)
        print(dic_week_hour_data)

        # 评论词云
        comment_lst = time_line['comment_notes']
        # print(comment_lst)
        comment_text_lst = []
        for text in comment_lst:
            # print(text['comment_text'].replace('\n','').replace(' ',''))
            comment_text_lst.append(text['comment_text'].replace('\n','').replace(' ',''))
        # print(comment_text_lst)
        big_comment_text = ''.join(comment_text_lst)
        # 分词
        wordlst = jieba.cut(big_comment_text)
        print(wordlst)
        # 取前100个分词最多的
        word_freq = Counter(wordlst).most_common(100)
        # print(word_freq)
        worddic = {tup[0]:tup[1] for tup in word_freq if len(tup[0])>=2}
        # print(worddic)
        # 发表评论的次数
        comment_freq = len(comment_lst)
        # print(comment_freq)

        # 返回词云对象
        word_cloud = make_wordcloud(worddic)


        return render_template('timeline.html',baseinfo=item,
                               first_tag_time=first_tag_time,
                               tags_data=tags_data,
                               month_data=dic_month_data,
                               day_data=dic_day_data,
                               hour_data=dic_hour_data,
                               week_data=dic_week_data,
                               week_hour=dic_week_hour_data,
                               max_freq=max_freq,
                               comments_num=comment_freq,
                               wordcloud_chart=word_cloud)

def get_first_tag_time(timeline):
    first_tag_time = {
        'first_like_user':extract_first_tag_time(timeline['like_users']),
        # 'join_time': self.user_data['join_time'],
        'first_like_user': extract_first_tag_time(timeline['like_users']),
        'first_share_note': extract_first_tag_time(timeline['share_notes']),
        'first_like_note': extract_first_tag_time(timeline['like_notes']),
        'first_like_coll': extract_first_tag_time(timeline['like_colls']),
        'first_like_nb': extract_first_tag_time(timeline['like_notebooks']),
        'first_comment': extract_first_tag_time(timeline['comment_notes']),
        'first_like_comment': extract_first_tag_time(timeline['like_comments']),
        # 'first_reward_note': extract_first_tag_time(timeline['reward_notes']),
    }
    return first_tag_time

# 抽取第一次
def extract_first_tag_time(lst):
    if len(lst) == 0:
        return None
    else:
        sorted_lst = sorted(lst, key=lambda dic:dic['time'])
        return sorted_lst[0]

# 拿到周的数据
def time_week(str_date):
    time_data = datetime.strptime(str_date,"%Y-%m-%d %H:%M:%S") # 转换成字符串类型
    # 拿到周的数据
    # print(time_data.weekday()) # [0-6]:0是周一，6是周日
    # 转化成周的形式
    weekday_dic = {0:"0周一",1:"1周二",2:"2周三",3:"3周四",4:"4周五",5:"5周六",6:"6周日"}
    return weekday_dic[time_data.weekday()]

def make_wordcloud(comm_data):
    '''
    由于echarts绘制词云图出现问题，用pyecharts绘制词云图
    :param comm_data:
    :return:
    '''
    name = comm_data.keys()
    value = comm_data.values()
    wordcloud = WordCloud(width='100%', height=600)
    wordcloud.add("", name, value, shape="diamond", word_size_range=[15, 120])
    return wordcloud.render_embed()


if __name__=='__main__':
    app.run(debug=True)