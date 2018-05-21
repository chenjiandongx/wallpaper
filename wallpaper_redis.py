#!/usr/bin/env python
# coding=utf-8

import os
import re

import requests
import redis

rd = redis.Redis(host="localhost")  # 本机作为 master
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}
SAVE_PATH = r"e:\wallpaper_redis"


class Wallpaper:

    def __init__(self, dir_path=None):
        self.dir_path = dir_path or SAVE_PATH  # 文件保存路径
        self.crawl_url = "http://sj.zol.com.cn{}"
        for url in self.get_urls():
            rd.sadd("urls", url)

    def mkdir(self, folder_name):
        """
        新建文件夹并切换到该目录下

        :param folder_name: 文件夹名称
        """
        path = os.path.join(SAVE_PATH, folder_name)
        # 如果目录已经存在就不用再次爬取了，去重，提高效率。存在返回 False，否则反之
        if not os.path.exists(path):
            os.makedirs(path)
            print(path)
            os.chdir(path)
            return True
        print("Folder has existed!")
        return False

    def save(self, src, name):
        """
        保存图片到本地

        :param src: 图片 src
        :param name: 保存图片名
        """
        try:
            img = requests.get(src, headers=HEADERS)
            with open(name + ".jpg", "ab") as f:
                f.write(img.content)
                print("{}.jpg save Successfully".format(name))
        except:
            pass

    def clear(self, dir_path):
        """
        删除空文件夹

        :param dir_path: 文件夹路径
        """
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                for d in os.listdir(dir_path):
                    path = os.path.join(dir_path, d)
                    if os.path.isdir(path):
                        # 递归删除空文件夹
                        self.clear(path)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print("remove the empty dir: {}".format(dir_path))

    def get_urls(self):
        """
        获取壁纸套图地址

        # 1080x1920(iphone6s plus)
        # 800x1280
        # 768x1280
        # 750x1334(iphone6)
        # 720x1280
        # 640x1336(iphone5s)
        """
        url = "http://sj.zol.com.cn/bizhi/1080x1920/{}.html"
        _urls = set()
        for url in [url.format(page) for page in range(1, 51)]:
            req = requests.get(url, headers=HEADERS).text
            for u in [
                self.crawl_url.format(u)
                for u in re.findall('<a class="pic" href="(.*?)"', req)
            ]:
                _urls.add(u)
        return _urls

    def run(self):
        """ 启动爬虫 """
        url = rd.spop("urls")
        while url:
            try:
                html = requests.get(url, headers=HEADERS).text
                # 壁纸套图名，也作文件夹名
                title = re.findall("<h1><a href=.*?>(.*?)</a.*?</h1>", html)[0]
                # 壁纸套图张数
                max_cnt_pattern = "</a><span>（(.*?)）</span>"
                max_cnt = re.findall(max_cnt_pattern, html)[0].split("/")[1]
                if self.mkdir(title):
                    # 按点击下一页循环下载
                    for _ in range(int(max_cnt)):
                        next_page = re.findall(
                            'class ="next" href="(.*?)"', html
                        )
                        img_url = re.findall(
                            'id="750x1334" href="(.*?)">750x1334</a>', html
                        )
                        # 像素未达到 750x1334 的不进行下载
                        img = img_url[0] if img_url else []
                        if img:
                            req = requests.get(
                                self.crawl_url.format(img), headers=HEADERS
                            ).text
                            img_src = re.findall('<img src="(.*?)"', req)[0]
                            self.save(img_src, img[-12:-5])
                        html = requests.get(
                            self.crawl_url.format(next_page[0]),
                            headers=HEADERS,
                        ).text
                url = rd.spop("urls")  # 再次弹出 url，循环爬取
            except Exception as e:
                print(e)
        self.clear(self.dir_path)  # 最后清除空文件夹


if __name__ == "__main__":
    Wallpaper().run()
