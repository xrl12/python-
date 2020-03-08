import urllib.request
import urllib.parse
import urllib.error
import random
import pymysql
import re
import os
import time


class DouTuLaSpider(object):
    def __init__(self):
        self.url = 'http://www.doutula.com/article/list/'
        self.hears = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        }
        self.img_heads = {
            # 'cookie': 'id=22946a925ec10025||t=1583400665|et=730|cs=002213fd48391982dc0ed28901',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'referer': 'https://www.doutula.com/article/detail/8108993',
            'x-client-data': 'CIm2yQEIorbJAQipncoBCM+vygEIvbDKAQiXtcoBCO21ygEIjrrKAQ==',

        }

        self.one_img_heads = {
            # 'Cookie':'id=22946a925ec10025||t=1583400665|et=730|cs=002213fd48391982dc0ed28901',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            # 'referer': 'https://www.doutula.com/article/detail/8108993',
            # 'x-client-data': 'CIm2yQEIorbJAQipncoBCM+vygEIvbDKAQiXtcoBCO21ygEIjrrKAQ==',

        }
        self.conn = pymysql.connect(host="localhost", user="root",
                                    password="123456", database="xici",
                                    charset="utf8")

        self.cursor = self.conn.cursor()
        self.proxy = self.get_proxy()
        self.i = 0

    # 获取代理的IP
    def get_proxy(self):

        sql = 'select * from proxy;'
        self.cursor.execute(sql)
        data1 = self.cursor.fetchall()
        ranom_data = random.choice(data1)
        proxy = {
            ranom_data[2]: str(ranom_data[0]) + ":" + str(ranom_data[1])
        }
        print('使用代理的IP是', proxy)
        return proxy

    # 创建自己的opener
    def own_opener(self):
        # 正在拼装自己的open方法
        proxyhandler = urllib.request.ProxyHandler(self.proxy)
        opener = urllib.request.build_opener(proxyhandler)
        return opener

    # 给主页发送请求
    def send_reqponse(self):
        # 主正在发送主页发送请求
        full_url = urllib.request.Request(url=self.url, headers=self.hears)
        opener = self.own_opener()
        try:
            response = opener.open(full_url)
        except urllib.error.HTTPError as error:
            print(error.code)
            print(error.reason)
            print(error.headers)

        except urllib.error.URLError as error:
            print(error.reason)
        self.get_pic_link(response.read().decode('utf8'))
        time.sleep(60)

    # 获取每套表情包的链接
    def get_pic_link(self, content):
        print('正在获取图片的链接和名字')
        # str = '<a href="http://www.doutula.com/article/detail/5322724" class="list-group-item random_list">'
        pattern = re.compile(
            r'<a.*?href="(http://www.doutula.com/article/detail/\d+?)"\sclass="list-group-item random_list.*?">\n<div class="random_title">(.*?)<div.*?</a>',
            re.S)
        result = pattern.findall(content)
        for phiz in result:
            print('这里是表情的链接', phiz[0])
            print('这里是表情的名字', phiz[1])
            self.mkdir(phiz[1])
            time.sleep(0.5)
            self.send_file_link(phiz[0], phiz[1])

    #    发送套图的请求
    def send_file_link(self, link, name):
        print('正在发送图片详情页的请求')
        full_url = urllib.request.Request(url=link, headers=self.img_heads)
        print('这里是图片详情页的链接', link)
        opener = self.own_opener()
        try:
            response = opener.open(full_url)
        except urllib.error.HTTPError as error:
            print(error.code)
            print(error.reason)
            print(error.headers)

        except urllib.error.URLError as error:
            print(error.reason)
        time.sleep(1)
        self.get_pic_file(response.read().decode('utf8'), name)

    # 获取单个图片
    def get_pic_file(self, content, name):
        print('正在匹配单个图片的链接')
        # <img referrerpolicy="no-referrer" src="http://ww3.sinaimg.cn/large/9150e4e5gy1gchjzb7m9xj201s01smwx.jpg" alt="不开心委屈" onerror="this.src='http://img.doutula.com/production/uploads/image/2020/03/04/20200304277893_VLZkuP.jpg'">
        pattern = re.compile(r'<div class="artile_des">.*?<img .*? src="(.*?)".*?>', re.S)
        result = pattern.findall(content)
        print('这里套图的名字是{}'.format(name), result)
        for link in result:
            self.send_one_img_link(link, name)
        self.i=0

    def send_one_img_link(self, link, name):
        print('正在获取单个图片的页面')
        full_url = urllib.request.Request(url=link, headers=self.one_img_heads)
        print('这里是单个图片的链接', link)
        opener = self.own_opener()
        try:
            response = opener.open(full_url)
        except urllib.error.HTTPError as error:
            print(error.code)
            print(error.reason)
            print(error.headers)

        except urllib.error.URLError as error:
            print(error.reason)
        self.write_file(response.read(), name)

    # 爬取的html文件，进行保存
    def write_file(self, content, name):
        print('正在保存文件')
        self.i += 1
        with open('/home/mrxu/PycharmProjects/WangLulZhiZhu/表情包/{}/{}'.format(name, name + str(self.i)), 'wb') as f:
            f.write(content)
            f.close()

    # 创建目录
    def mkdir(self, name):
        path = '/home/mrxu/PycharmProjects/WangLulZhiZhu/表情包/' + name
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)

    def main(self):
        self.send_reqponse()


if __name__ == '__main__':
    dotu = DouTuLaSpider()
    dotu.main()
