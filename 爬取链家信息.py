import csv
import re
import urllib.parse
from json import loads
from random import choice
from time import sleep
import requests
from lxml import etree


class LinaJiaSpider(object):
    def __init__(self):
        self.url = 'https://bj.lianjia.com/ershoufang/'
        self.heads = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        }
        self.proxy = self.get_proxy()
        self.house_info_dict = {}
        self.scv_f = open('链家数据.csv', 'a')
        self.scv_head = ['售价', '每平米', '小区名称', '所处区域', '房屋户型', '所在楼层', '建筑面积', '户型结构', '套内面积', '建筑类型', '房屋朝向', '建筑结构',
                         '装修情况', '梯户比例', '供暖方式', '配备电梯', '产权年限', '房屋用途', '交易权属']
        self.write = csv.DictWriter(self.scv_f, self.scv_head)

    def send_response(self, url):
        print('-------------------------------------------->正在发送到路由是{}'.format(url))
        sleep(3)
        response = requests.get(url=url, headers=self.heads, proxies=self.proxy)
        return response.text

    def parse(self, content):
        print('-------------------------------------------->正在解析列表页数据')
        html = etree.HTML(content)
        href_list = html.xpath("//div[@data-role='ershoufang']//a/@href")
        for href in href_list:
            # 发送区域的路由
            url = urllib.parse.urljoin(self.url, href)
            area_response = self.send_response(url)
            self.list_parse(area_response)

    # 对下一页的路由进行解析和拼接
    def list_parse(self, area_response):
        # 获取列表页的路由
        pattern = re.compile(r'<a class="noresultRecommend img LOGCLICKDATA"\shref="(.*?)".*?>', re.S)
        detail_url = pattern.findall(area_response)
        for url in detail_url:
            # 发送详情页面的路由
            response = self.send_response('https://bj.lianjia.com/ershoufang/101103824563.html')
            self.detail_parse(response)
        print('-------------------------------------------->正在解析下一页的路由')
        guizie = """<div class="page-box house-lst-page-box" comp-module='page' page-url="(.*?){page}"page-data='(.*?)'>"""
        pattern = re.compile(guizie, re.S)
        next_page = pattern.findall(area_response)
        next_url = str(next_page[0][0]).replace('{page}', '') + str(loads(next_page[0][1])['curPage'] + 1)
        all_url = urllib.parse.urljoin(self.url, next_url)
        # 获取下一页的路由
        if loads(next_page[0][1])['curPage'] + 1 <= loads(next_page[0][1])['totalPage']:
            # 发送列表下一页的路由
            print('正在第{}页'.format(loads(next_page[0][1])['curPage'] + 1))
            response = self.send_response(all_url)
            self.list_parse(response)

    def detail_parse(self, content):
        print('-------------------------------------------->正在解析详情页的数据')
        with open('详情页.html', 'w') as f:
            f.write(content)
            f.close()
        html = etree.HTML(content)
        price = html.xpath("//div[@class='price ']//span/text()")
        community_name = html.xpath("//div[@class='communityName']/a[1]/text()")
        area_name = html.xpath("//span[@class='info']/a/text()")
        house_info = html.xpath("//div[@class='base']//div[@class='content']/ul/li/text()")
        house_info_key = html.xpath("//div[@class='base']//div[@class='content']/ul/li/span[1]/text()")
        house_user = html.xpath("//div[@class='transaction']//div[@class='content']/ul/li[4]//span/text()")
        Trading_ownership = html.xpath("//div[@class='transaction']//div[@class='content']/ul/li[2]//span[2]/text()")
        #  判断数据是否存在，如果存在就过，不存在自己添加未知
        if '房屋户型' not in house_info_key:
            house_info.insert(0, '暂无数据')
        if '所在楼层' not in house_info_key:
            house_info.insert(1, '暂无数据')
        if '建筑面积' not in house_info_key:
            house_info.insert(2, '暂无数据')
        if '户型结构' not in house_info_key:
            house_info.insert(3, '暂无数据')
        elif '套内面积' not in house_info_key:
            house_info.insert(4, '暂无数据')
        elif '建筑类型' not in house_info_key:
            house_info.insert(5, '暂无数据')
        elif '房屋朝向' not in house_info_key:
            house_info.insert(6, '暂无数据')
        elif '建筑结构' not in house_info_key:
            house_info.insert(7, '暂无数据')
        if '装修情况' not in house_info_key:
            house_info.insert(8, '暂无数据')
        if '梯户比例' not in house_info_key:
            house_info.insert(9, '暂无数据')
        if '供暖方式' not in house_info_key:
            house_info.insert(10, '暂无数据')
        if '配备电梯' not in house_info_key:
            house_info.insert(11, '暂无数据')
        if '产权年限' not in house_info_key:
            house_info.insert(12, '暂无数据')

        print(house_info)
        print(house_info_key)
        self.house_info_dict['售价'] = str(price[0]) + price[1]
        self.house_info_dict['每平米'] = price[2]
        self.house_info_dict['小区名称'] = community_name[0]
        self.house_info_dict['所处区域'] = ','.join(area_name)
        self.house_info_dict['房屋户型'] = house_info[0]
        self.house_info_dict['所在楼层'] = house_info[1]
        self.house_info_dict['建筑面积'] = house_info[2]
        self.house_info_dict['户型结构'] = house_info[3]
        self.house_info_dict['套内面积'] = house_info[4]
        self.house_info_dict['建筑类型'] = house_info[5]
        self.house_info_dict['房屋朝向'] = house_info[6]
        self.house_info_dict['建筑结构'] = house_info[7]
        self.house_info_dict['装修情况'] = house_info[8]
        self.house_info_dict['梯户比例'] = house_info[9]
        self.house_info_dict['供暖方式'] = house_info[10]
        self.house_info_dict['配备电梯'] = house_info[11]
        self.house_info_dict['产权年限'] = house_info[12]
        self.house_info_dict['房屋用途'] = house_user[0]
        self.house_info_dict['交易权属'] = Trading_ownership[0]
        self.write_csv()

    def write_csv(self):
        print(self.house_info_dict)
        self.write.writerow(self.house_info_dict)
        self.house_info_dict.clear()

    def get_proxy(self):
        print('-------------------------------------------->正在获取代理')
        file = open('xici代理.csv', 'r')
        data = file.readlines()
        proxy = choice(data)
        new_proxy = str(proxy).split(',')
        use_proxy = {new_proxy[2].replace('\n', ''): str(new_proxy[0]) + ':' + str(new_proxy[1])}
        print('使用的代理是：', use_proxy)
        return use_proxy


if __name__ == '__main__':
    ljs = LinaJiaSpider()
    response = ljs.send_response(ljs.url)
    ljs.parse(response)
