# -*- coding: utf-8 -*-
#coding=utf-8
#import sys
#from imp import reload
import scrapy
from pymongo import *
import re

#reload(sys)
#sys.setdefaultencoding('utf-8')
#print(sys.getdefaultencoding())

class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['movie.douban.com']
    #start_urls = ['http://movie.douban.com/']

    client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client.douban
    collection = db.col_movie

    headers_movie = {
        "Host": "movie.douban.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://read.douban.com/reader/ebook/13606087/",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    }

    def start_requests(self):
        #url = 'https://movie.douban.com/subject/22263645/'
        #查询上次中断的id
        cnt = collection.find().count()
        #cnt = 22263644
        for id in range(cnt+1,22263646):
            find_one = self.collection.find_one({'_id':id})
            if find_one :
                if find_one['http_status'] == 200 :
                    #之前已经爬取过，跳出
                    print("find subject id %d,http status 200,next\n" % id)
                    continue
                else:
                    #之前爬取的状态非200，重试
                    print("find subject id %d,http status %d,remove\n" % (id,find_one['http_status']))
                    self.collection.remove({'_id':id})

            url = 'https://movie.douban.com/subject/' + str(id) + '/'
            yield scrapy.Request(url,headers=self.headers_movie,callback=self.parse,encoding='utf-8',meta={'id':id,'handle_httpstatus_all':True})

    def parse(self, response):
        item = {}
        #subject id
        item['_id'] = response.meta['id']
        #doban url
        item['url'] = response.url
        #http status
        item['http_status'] = response.status
        if item['http_status'] != 200 :
            #save to mongo
            self.collection.insert(item)
            return

        #电影名
        item['itemreviewed'] = response.xpath('//*[@id="content"]/h1/span[1]/text()').extract_first().strip()
        #年份
        item['year'] = response.xpath('//*[@id="content"]/h1/span[2]/text()').extract_first().strip()
        #海报
        item['image'] = response.xpath('//*[@id="mainpic"]/a/img/@src').extract_first().strip()
        #评分
        item['rating_num'] = float(response.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()').extract_first(default='0').strip())
        #评价数
        item['votes'] = float(response.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/div/div[2]/a/span/text()').extract_first(default='0').strip())
        #标签
        item['tags'] = []
        tags = response.xpath('//*[@id="content"]/div[2]/div[2]/div[4]/div/a')
        for sel in tags:
            tag = sel.xpath('text()').extract_first().strip()
            item['tags'].append(tag)
        #info
        info = response.xpath('//div[@id="info"]').extract_first()
        pattern = re.compile(r"<span class=\"pl\">(.*)<br>")
        pattern2_0 = re.compile(r"(.*?)</span>(.*)")
        pattern3 = re.compile(r">(.*?)<")
        find = re.findall(pattern,info)

        item['info'] = []

        for i in find: 
            find2 = re.search(pattern2_0,i)
            if find2:
                key = find2.group(1).strip(' ').strip(':')
                find3 = re.findall(pattern3,find2.group(2))
                attrs = []
                if not find3:
                    attr = find2.group(2).strip(' ')
                    attrs.append(attr)
                else:
                    for iii in find3:
                        attr = iii.strip(' ').strip('/')
                        if attr:
                            attrs.append(attr)
            item['info'].append({'key':key,'value':attrs})
        #电影简介
        item['summary'] = []
        summary = response.xpath('//*[@id="link-report"]/span[1]/text()').extract(default='')
        for sel in summary:
            item['summary'].append(sel.strip('\n').strip(' '))

        #save to mongo
        self.collection.insert(item)
        pass
