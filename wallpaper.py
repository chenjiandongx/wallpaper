#!/usr/bin/env python
# coding=utf-8


import os
import re
import threading
import time
from multiprocessing import Pool, cpu_count

import requests

# 图片存放路径
SAVE_PATH = r"D:\wallpaper"
CRAWL_URL = "http://sj.zol.com.cn{}"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}


def mkdir(folder_name):
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


def save_images(src, name):
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


def clear(dir_path):
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
                    clear(path)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
            print("remove the empty dir: {}".format(dir_path))


def get_urls():
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
            CRAWL_URL.format(u)
            for u in re.findall('<a class="pic" href="(.*?)"', req)
        ]:
            _urls.add(u)
    return _urls


lock = threading.Lock()


def run(url):
    """
    启动爬虫
    """
    try:
        html = requests.get(url, headers=HEADERS).text
        # 壁纸套图名，也作文件夹名
        title = re.findall("<h1><a href=.*?>(.*?)</a.*?</h1>", html)[0]
        # 壁纸套图张数
        max_cnt = re.findall("</a><span>（(.*?)）</span>", html)[0].split("/")[1]
        with lock:
            if not mkdir(title):
                return
            # 按点击下一页循环下载
            for _ in range(int(max_cnt)):
                next_page = re.findall('class ="next" href="(.*?)"', html)
                img_url = re.findall(
                    'id="750x1334" href="(.*?)">750x1334</a>', html
                )
                # 像素未达到 750x1334 的不进行下载
                img = img_url[0] if img_url else []
                if img:
                    req = requests.get(
                        CRAWL_URL.format(img), headers=HEADERS
                    ).text
                    img_src = re.findall('<img src="(.*?)"', req)[0]
                    save_images(img_src, img[-12:-5])
                html = requests.get(
                    CRAWL_URL.format(next_page[0]), headers=HEADERS
                ).text

    except Exception as e:
        print(e)


if __name__ == "__main__":
    urls = get_urls()
    pool = Pool(processes=cpu_count())
    try:
        pool.map(run, urls)
    except:
        time.sleep(30)
        pool.map(run, urls)
    # 由于有些套图图片像素大小未达到要求，文件夹为空需要清理
    clear(SAVE_PATH)
