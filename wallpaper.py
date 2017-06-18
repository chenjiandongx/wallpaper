import os
import re
import threading
import time
from multiprocessing import Pool, cpu_count
import requests

dir_path = r"e:\wallpaper"      # 图片存放路径
fmt = "http://sj.zol.com.cn{}"
headers = {'X-Requested-With': 'XMLHttpRequest',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/56.0.2924.87 Safari/537.36'}

def mkdir(folder_name):
    """ 新建文件夹并切换到该目录下 """
    path = os.path.join(dir_path, folder_name)
    # 如果目录已经存在就不用再次爬取了，去重，提高效率。存在返回 False，否则反之
    if not os.path.exists(path):
        os.makedirs(path)
        print(path)
        os.chdir(path)
        return True
    print("Folder has existed!")
    return False

def save(src, name):
    """ 保存图片到本地 """
    try:
        img = requests.get(src, headers=headers)
        with open(name + ".jpg", 'ab') as f:
            f.write(img.content)
            print("Success!")
    except:
        print("Failed!")

def clear(dir):
    """ 删除空文件夹 """
    if os.path.exists(dir):
        if os.path.isdir(dir):
            for d in os.listdir(dir):
                path = os.path.join(dir, d)
                if os.path.isdir(path):
                    clear(path)     # 递归删除空文件夹
        if not os.listdir(dir):
            os.rmdir(dir)
            print("remove the empty dir: {}".format(dir))

lock = threading.Lock()

def geturls():
    """ 获取壁纸套图地址 """
    # 1080x1920(iphone6s plus)
    # 800x1280
    # 768x1280
    # 750x1334(iphone6)
    # 720x1280
    # 640x1336(iphone5s)
    url = "http://sj.zol.com.cn/bizhi/1080x1920/{}.html"
    _urls = set()
    for url in [url.format(page) for page in range(1, 51)]:
        r = requests.get(url, headers=headers).text
        for u in [fmt.format(u) for u in re.findall('<a class="pic" href="(.*?)"', r)]:
            _urls.add(u)
    return _urls

def run(url):
    """ 启动爬虫 """
    try:
        result = requests.get(url, headers=headers).text
        # 壁纸套图名，也作文件夹名
        title = re.findall('<h1><a href=.*?>(.*?)</a.*?</h1>', result)[0]
        # 壁纸套图张数
        max_cnt = re.findall('</a><span>（(.*?)）</span>', result)[0].split("/")[1]
        with lock:
            if mkdir(title):
                # 按点击下一页循环下载
                for _ in range(int(max_cnt)):
                    next_page = re.findall('class ="next" href="(.*?)"', result)[0]
                    img_url = re.findall('id="750x1334" href="(.*?)">750x1334</a>', result)
                    # 像素未达到 750x1334 的不进行下载
                    img = img_url[0] if img_url else []
                    if img:
                        r = requests.get(fmt.format(img), headers=headers).text
                        img_src = re.findall('<img src="(.*?)"', r)[0]
                        save(img_src, img[-12:-5])
                    result = requests.get(fmt.format(next_page), headers=headers).text
    except Exception as e:
        print(e)

if __name__ == "__main__":
    urls = geturls()
    pool = Pool(processes=cpu_count())
    try:
        pool.map(run, urls)
    except:
        time.sleep(30)
        pool.map(run, urls)
    # clear(dir_path)   # 由于有些套图图片像素大小未达到要求，文件夹为空需要清理