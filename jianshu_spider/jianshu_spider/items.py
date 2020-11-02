# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JianshuSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    nickname = scrapy.Field() # 昵称
    slug = scrapy.Field() # 短网址
    head_pic = scrapy.Field() # 头像地址
    gender = scrapy.Field() # 性别
    is_contract = scrapy.Field() # 简书签约作者
    following_num = scrapy.Field() # 关注人数
    followers_num = scrapy.Field() # 粉丝数
    articles_num = scrapy.Field() # 文章数
    words_num = scrapy.Field() # 字数
    be_liked_num = scrapy.Field() # 收获喜欢
