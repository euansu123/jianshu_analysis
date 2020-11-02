import time

import requests
from fake_useragent import UserAgent
from lxml import etree
from jianshu_flask.config import *
import pymongo

BASE_HEADERS = {
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Host': 'www.jianshu.com',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'text/html, */*; q=0.01',
    'User-Agent': UserAgent().random,
    'Connection': 'keep-alive',
    'Referer': 'http://www.jianshu.com',
}

def retry(attempt):
    '''
    函数重试装饰器
    :param attempt:  函数重试次数，
    将该装饰器装饰于任何目标函数，目标函数执行时会进行给定次数的重试
    '''
    def decorator(func):
        def wrapper(*args, **kw):
            att = 0
            while att < attempt:
                try:
                    time.sleep(5)
                    return func(*args, **kw)
                except Exception as e:
                    att += 1
                    print('第%s次出现了错误' % att, e)
        return wrapper
    return decorator



class GetUserInfo:

    def __init__(self,slug):
        self.slug = slug
        # 抓取动态采用不同headers，带“X-PJAX”：“true”返回动态加载片段，加Referer反盗链
        AJAX_HEADERS = {"Referer": f"http//:www.jianshu.com/u/{self.slug}",
                        "X-PJAX": "true"}
        self.headers = dict(BASE_HEADERS,**AJAX_HEADERS)

        # 初始化盛数据的容器：timeline
        self.timeline = {
            'comment_notes': [],
            'like_notes': [],
            'reward_notes': [],
            'share_notes': [],
            'like_users': [],
            'like_colls': [],
            'like_comments': [],
            'like_notebooks': [],
        }

        self.en_parent_tags = ('comment_notes', 'like_notes', 'reward_notes', 'share_notes',
                          'like_users', 'like_colls', 'like_comments', 'like_notebooks')

        self.zh_parent_tags = ['发表评论', '喜欢文章', '赞赏文章', '发表文章', '关注用户', '关注专题', '点赞评论', '关注文集']

    def tags_data(self):
        tags_name_lis = [{'name':tag_name} for tag_name in self.zh_parent_tags]
        tags_value_lis = [{'value':len(self.timeline[tag_en_name])} for tag_en_name in self.en_parent_tags]
        tags_data = [dict(tags_name_lis[i],**tags_value_lis[i]) for i in range(len(self.en_parent_tags))]
        return tags_data

    def get_tag_month_data(self):
        all_time_lis = []
        for tag_en_name in self.en_parent_tags:
            timelis = [dic['time'] for dic in self.timeline[tag_en_name]]
            all_time_lis.extend(timelis)
            # print(all_time_lis)
            return all_time_lis

    # @retry(5)
    def get_user_info(self):
        url = f'https://www.jianshu.com/u/{self.slug}'
        response = requests.get(url,headers=BASE_HEADERS)
        if response.status_code == 404:
            '''经测试，出现404时都是因为用户被封禁或注销，即显示：
            您要找的页面不存在.可能是因为您的链接地址有误、该文章已经被作者删除或转为私密状态。'''
            return None
        else:
            tree = etree.HTML(response.text)

            div_main_top = tree.xpath('//div[@class="main-top"]')[0]
            nickname = div_main_top.xpath('.//div[@class="title"]//a/text()')[0]
            head_pic = div_main_top.xpath('.//a[@class="avatar"]//img/@src')[0]

            # 检查用户填写的性别信息。1：男  -1：女  0：性别未填写
            if div_main_top.xpath('.//i[@class="iconfont ic-man"]'):
                gender = 1
            elif div_main_top.xpath('.//i[@class="iconfont ic-woman"]'):
                gender = -1
            else:
                gender = 0

            # 判断该用户是否为签约作者。is_contract为1是简书签约作者，为0则是普通用户
            if div_main_top.xpath('.//i[@class="iconfont ic-write"]'):
                is_contract = 1
            else:
                is_contract = 0

            # 取出用户文章及关注量
            info = div_main_top.xpath('.//li//p//text()')

            item = {'nickname': nickname,
                    'slug': self.slug,
                    'head_pic': head_pic,
                    'gender': gender,
                    'is_contract': is_contract,
                    'following_num': int(info[0]),
                    'followers_num': int(info[1]),
                    'articles_num': int(info[2]),
                    'words_num': int(info[3]),
                    'be_liked_num': int(info[4]),
                    'update_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    }
        return item

    def get_user_timeline(self,last_time='',max_id = None,page=1):
        if max_id == None:
            url = f'https://www.jianshu.com/users/{self.slug}/timeline'
        else:
            url = f'https://www.jianshu.com/users/{self.slug}/timeline?max_id={max_id}&page={page}'

        response = requests.get(url,headers=self.headers)
        # print(response.text)
        tree = etree.HTML(response.text)
        li_lis = tree.xpath('//li')
        # 拿到最后一个id
        # lastli_id = li_lis[-1].xpath('./@id')
        try:
            lastli_id = li_lis[-1].xpath('./@id')
        except:
            # self.timeline['join_time'] = '~走丢了~'
            return None
        max_id_num = int(lastli_id[0].replace('feed-', '')) - 1
        # print(max_id_num)
        # print(lastli_id)
        count = 0
        for li in li_lis:
            count += 1
            # data_type = li.xpath('.//span/@data-type') # 判断作者的行为，需要在匹配的路径前加一个·是要从当前节点出发
            # 作者产生行为的时间：mark_time
            mark_time = li.xpath('.//@data-datetime')[0]
            mark_time = mark_time.split('+')[0].replace('T',' ')
            # print(mark_time)
            # 拿到最近一条的动态，实现断点续传
            if page == 1 and count == 1:
                self.timeline['last_time'] = mark_time
                print('第一条动态',self.timeline['last_time'])

            if mark_time <= last_time:
                return None


            if li.xpath('.//span[@data-type="share_note"]'):
                share_note = {}
                share_note['time'] = mark_time
                share_note['note_id'] = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                # print(share_note['note_id'])
                self.timeline['share_notes'].append(share_note)
                print('发表了文章',share_note)
            elif li.xpath('.//span[@data-type="comment_note"]'):
                comment_note = {}
                comment_note['time'] = mark_time
                comment_note['note_id'] = self.get_href_id(li)
                comment_note['comment_text'] = self.get_comment_text(li)
                print('发表了评论',comment_note)
                self.timeline['comment_notes'].append(comment_note)
            elif li.xpath('.//span[@data-type="like_note"]'):
                like_note = {}
                like_note['time'] = mark_time
                like_note['note_id'] = self.get_href_id(li)
                print('喜欢了文章',like_note)
                self.timeline['like_notes'].append(like_note)
            elif li.xpath('.//span[@data-type="reward_note"]'):
                reward_note = {}
                reward_note['note_id'] = self.get_href_id(li)
                print('赞赏了文章', reward_note)
                self.timeline['reward_notes'].append(reward_note)
            elif li.xpath('.//span[@data-type="like_user"]'):
                like_user = {}
                like_user['time'] = mark_time
                like_user['slug'] = self.get_href_id(li)
                print('关注作者', like_user)
                self.timeline['like_users'].append(like_user)
            elif li.xpath('.//span[@data-type="like_coll"]'):
                like_coll = {}
                like_coll['time'] = mark_time
                like_coll['coll_id'] = self.get_href_id(li)
                print('关注专题', like_coll)
                self.timeline['like_colls'].append(like_coll)
            elif li.xpath('.//span[@data-type="like_comment"]'):
                like_comment = {}
                like_comment['time'] = mark_time
                like_comment['comment_text'] = self.get_comment_text(li)
                like_comment['slug'] = self.get_like_comment_slug(li)
                like_comment['note_id'] = self.get_like_comment_note_id(li)
                print('赞了评论', like_comment)
                self.timeline['like_comments'].append(like_comment)
            elif li.xpath('.//span[@data-type="like_notebook"]'):
                like_notebook = {}
                like_notebook['time'] = mark_time
                like_notebook['notebook_id'] = self.get_href_id(li)
                print('关注文集', like_notebook)
                self.timeline['like_notebooks'].append(like_notebook)
            elif li.xpath('.//span[@data-type="join_jianshu"]'):
                join_time = mark_time
                print('加入简书', join_time)
                self.timeline['join_time'] = join_time
                return None # 此处应该return，否则会产生越界的错误
        self.get_user_timeline(max_id=max_id_num,page=page+1)

    def get_obj_title(self, li):
        '''获取文章标题'''
        title = li.xpath('.//a[@class="title"]/text()')[0]
        return title

    def get_href_id(self, li):
        '''获取文章id'''
        href_id = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
        return href_id

    def get_comment_text(self, li):
        '''获取发表评论的内容'''
        like_comment_text = ''.join(li.xpath('.//p[@class="comment"]/text()'))
        return like_comment_text

    def get_like_comment_slug(self, li):
        '''获取赞了用户评论的slug'''
        like_comment_slug = li.xpath('.//div[@class="origin-author single-line"]//@href')[0].split('/')[-1]
        return like_comment_slug

    def get_like_comment_note_id(self, li):
        '''获取评论文章的id'''
        like_comment_note_id = li.xpath('.//div[@class="origin-author single-line"]//@href')[1].split('/')[-1]
        return like_comment_note_id




# if __name__ == '__main__':
    # gui = GetUserInfo('6d6ea5dd47a4')
    # r = gui.get_user_info()
    # print(r)
    # p = gui.get_user_timeline()
    # print(s)
    # s = gui.get_tag_month_data()