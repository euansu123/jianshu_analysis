import pymongo
from jianshu_flask.config import *
import pandas as pd

class PandasAnlysisUserinfo:
    def __init__(self,slug):
        self.client = pymongo.MongoClient(MONGO_HOST,MONGO_PORT)
        self.db = self.client[MONGO_TABLE]
        self.slug = slug
        self.en_parent_tags = ('comment_notes', 'like_notes', 'reward_notes', 'share_notes',
                               'like_users', 'like_colls', 'like_comments', 'like_notebooks')

        self.zh_parent_tags = ['发表评论', '喜欢文章', '赞赏文章', '发表文章', '关注用户', '关注专题', '点赞评论', '关注文集']

        userdata = self.db['user_timeline'].find_one({'slug':self.slug})
        # df1 = pd.DataFrame(userdata['comment_notes'])
        # df2 = pd.DataFrame(userdata['like_notes'])
        # dflst = [df1,df2]
        # 设置显示所有列
        pd.set_option('display.max_columns', None)
        # self.df = pd.concat(dflst)
        # print(self.df)
        # 取出所有列
        dfLst = []
        for columns in self.en_parent_tags:
            df = pd.DataFrame(userdata[columns])
            dfLst.append(df)
        self.df = pd.concat(dfLst)
        # print(self.df)

    def pd_get_month_data(self):
        timelst = pd.to_datetime(list(self.df.time))
        # print(timelst)
        # 拿到了时间的series
        series = pd.Series([1]*len(timelst),index=timelst)
        # print(series)
        # 按照月分进行动态累加
        timeMonth = series.resample('1M').sum()
        # print(timeMonth[timeMonth>0]) # 如果当月动态为0，则去除
        # print(timeMonth[timeMonth>0].index) # 以series作为索引，去除掉不发动态的月份
        lstMonth = [x.strftime('%Y-%m') for x in timeMonth[timeMonth>0].index]
        # print(lstMonth)
        lstFreq = list(timeMonth[timeMonth>0].values)
        # print(lstFreq)
        dic_month_data = {
            'month_line':lstMonth,
            'month_freqency':list(map(int,lstFreq))
        }

        return dic_month_data

    def pd_get_day_data(self):
        timelst = pd.to_datetime(list(self.df.time))
        # print(timelst)
        # 拿到了时间的series
        series = pd.Series([1] * len(timelst), index=timelst)
        # print(series)
        # 按照月分进行动态累加
        timeDay = series.resample('1D').sum()
        # print(timeMonth[timeMonth>0]) # 如果当月动态为0，则去除
        # print(timeMonth[timeMonth>0].index) # 以series作为索引，去除掉不发动态的月份
        lstDay = [x.strftime('%Y-%m-%d') for x in timeDay[timeDay > 0].index]
        # print(lstMonth)
        lstFreq = list(timeDay[timeDay > 0].values)
        # print(lstFreq)
        dic_day_data = {
            'day_line': lstDay,
            'day_freqency': list(map(int, lstFreq))
        }

        return dic_day_data

    def pd_get_hour_data(self):
        dti = pd.to_datetime(self.df.time).to_frame() #转化为dataframe

        lstHour = dti.groupby(dti['time'].map(lambda x: x.hour)).count() # 按照小时进行统计

        lst_freqency = [int(item[0]) for item in lstHour[lstHour > 0].values] # 获得统计的次数

        hourlst = [str(int(x)).rjust(2, '0') + ':00' for x in lstHour[lstHour > 0].index] # 获得小时
        # print(lstDay)
        dic_hour_data = {'hour_line': hourlst, 'hour_freqency': lst_freqency}

        return dic_hour_data

    def pd_get_week_data(self):
        dtime = pd.to_datetime(self.df.time).to_frame()
        # print(dti)
        timeDay = dtime.groupby(dtime['time'].map(lambda x: x.dayofweek)).count()
        # print(timeDay)
        # 获得了按周的分布状态
        # lst_freqency = str([item[0] for item in timeDay[timeDay>0].values])
        lst_freqency = [int(item[0]) for item in timeDay[timeDay > 0].values]
        # print(str(lst_freqency))
        week_day_dict = {0: '周一', 1: '周二', 2: '周三', 3: '周四',
                         4: '周五', 5: '周六', 6: '周日', }
        daylst = [week_day_dict[x] for x in timeDay[timeDay > 0].index]
        # print(daylst)
        dic_week_data = {
            'week_line': daylst,
            'week_freqency': lst_freqency
        }
        return dic_week_data

    def pd_get_week_hour_data(self):
        dtime = pd.to_datetime(self.df.time).to_frame()
        # print(dti)
        # gg = dtime.groupby([dtime['time'].map(lambda x:x.dayofweek).rename('week'),dtime['time'].map(lambda x:x.hour).rename('hour')]).count()
        # 得到一个groupsby对象，希望循环得到星期和小时时间
        Daytime = dtime.groupby([dtime['time'].map(lambda x:x.dayofweek).rename('week'),dtime['time'].map(lambda x:x.hour).rename('hour')])
        Timecount = Daytime.count() # 统计的是次数
        max_freq = 0 # 统计最大的次数，用于eachres显示
        dic_week_hour_data = []
        for name,_ in Daytime:
            freq = Timecount.loc[name].values[0]
            if freq>max_freq:
                max_freq = freq
            each = [int(name[1]),int(name[0]),int(freq)]
            dic_week_hour_data.append(each)
        # print(day_hour_times)
        return max_freq,dic_week_hour_data


if __name__=="__main__":
    pau = PandasAnlysisUserinfo('53e7dea95963')
    # dic_month_data = pau.pd_get_month_data()
    # print(dic_month_data)
    # dic_day_data = pau.pd_get_day_data()
    # print(dic_day_data)
    # h = pau.pd_get_hour_data()
    # print(h)
    # r = pau.pd_get_week_data()
    # print(r)
    # pau.pd_get_week_hour_data()
    max_freq, dic_week_hour_data = pau.pd_get_week_hour_data()
    print(max_freq)
    print(dic_week_hour_data)
