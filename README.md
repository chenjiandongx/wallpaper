# zol 手机壁纸爬虫

这两天在找手机壁纸，不过发现一张一张来效率太低。话不多说，爬虫在手，天下我有！  

爬取网站：[http://sj.zol.com.cn/bizhi/](http://sj.zol.com.cn/bizhi/)  

至于为什么选这个 zol 的手机壁纸网站，没办法，某度搜索出来第一个，树大招风！  

代码用 Python 写的，第三方类库只用了 requests，老少皆宜。匹配只用了正则表达式。利用多进程提高爬取速度。

壁纸大小为 750 * 1334（iphone6 的分辨率），大小可在代码里自行更改，最高的分辨率为 1080 * 1920（iphone6s plus 的分辨率）。  

总共爬取了 **420** 套，共 **3941** 张壁纸。  

![wallpaper_0](https://github.com/chenjiandongx/wallpaper/blob/master/images/wallpaper_0.png)  

具体情况如下图，以套图为单位存放在不同的文件夹  

![wallpaper_1](https://github.com/chenjiandongx/wallpaper/blob/master/images/wallpaper_1.png)  

囊括了各种风格的壁纸！！

然而，事情到这里还没有结束。这两天看了 redis 的文档，就想利用 redis 来搞个简单的分布式爬虫。前期工作的下载和配置 redis 我就不说了。核心逻辑是先将所有连接存入到本机的 redis 数据库里，本机作为 master。然后其他 slave 连接到 master 分配任务干活。但是，你以为我既没有另外一台电脑也没有钱购买虚拟主机这件事我会告诉你？最后就只用了本机爬...  ，anyway，最后也同样把所有的套图都爬下来了。这部分代码在 wallpaper_redis.py 里。  

壁纸已打包上传到百度云里：链接: [https://pan.baidu.com/s/1boZ6XTP](https://pan.baidu.com/s/1boZ6XTP) 密码: q8k6  

为了深入贯彻党提倡的二十四字社会主义核心价值观，请允许我先大家安利下面这张壁纸  

![wallpaper_2](https://github.com/chenjiandongx/wallpaper/blob/master/images/wallpaper_2.jpg)

**永远热血，永远热泪盈眶！**


### License

MIT [© chenjiandongx](https://github.com/chenjiandongx)
