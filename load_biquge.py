# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    load_biquke.py
   Description：
-------------------------------------------------
__author__ = 'ZH'
"""
import requests
from bs4 import BeautifulSoup
import re,os
import logging
import sys
sys.setrecursionlimit(1000000)#防止迭代超过上限报错
import MainLoggerConfig

MainLoggerConfig.setup_logging(default_path="./logs.yaml")

class load_biquge(object):

    logger = logging.getLogger()

    def __init__(self,mother_url,dir="./data"):
        self.storyName=""#存储小说名
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.dir = dir#保存路径
        self.mother_url=mother_url#文章链接

    def html_parse(self,url):
        '''
        解析网页返回beautifulsoap对象
        :param url: url
        :return: beautifulsoap对象
        '''
        content=requests.get(url).content.decode("gbk")
        return BeautifulSoup(content, "html.parser")

    def get_save_page(self,page_url):
        '''
        获取一个章节链接，保存为txt文件
        :param page_url: 章节链接
        :return:
        '''
        text=[]
        self.logger.info("load a page_url:%s"%page_url)
        page_content=self.html_parse(page_url)
        title=page_content.find("h1").string
        txt_content=page_content.find("div",id="content").stripped_strings
        for i in txt_content:
            if re.search(r"52bqg\.com",i):
                continue
            text.append(i)
        else:
            with open("{}/{}".format(self.dir,title+ ".txt"), "w+",encoding="utf-8") as f:
                f.write("\n".join(text))
            self.logger.debug("Successfully downloaded a file:%s.txt" % title)

    def get_page_url(self):
        '''
        解析目标小说链接，返回章节链接
        :return: 返回章节链接
        '''
        mode_page=self.html_parse(self.mother_url)
        self.storyName=mode_page.find("h1").string
        ddList = mode_page.find_all("dd")
        page_url =["".join([self.mother_url,dd.find("a").get("href")]) for dd in ddList if dd.find("a")]
        return page_url

    @staticmethod
    def arrange(filename):
        '''
        用于转换指定汉字章节对应的数字排名，例如第一百一十一章，则返回111；
        :param filename:
        :return:
        '''
        matchs = {"一": "1", "二": "2","两":"2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9","零":"0"}
        string = ""
        file_num= filename.split()[0]
        str_num=re.findall(r"第(.*)章", file_num)[0]
        for k in str_num:
            if k in matchs:
                string += matchs[k]
            if k.isdigit():
                string += k
        if str_num[0]=="十":
            string="1"+string
        if str_num[-1] == "十":
            string += "0"
        if str_num[-1] == "百":
            string += "0" * 2
        if str_num[-1] == "千":
            string += "0" * 3
        if str_num[-1] == "万":
            string += "0" * 4
        return int(string)

    def filewrite(self):
        '''
        过滤章节，筛选出需要的章节，根据章节与章节排名排序，逐一合并写入txt中
        :return:
        '''

        kwags = {}
        os.chdir(self.dir)

        self.logger.info("Start to filter arctcles.....")

        for filename in os.listdir("."):
            if not re.search("(^第.*章.*)", filename):
                self.logger.info("filter:%s"%filename)
                os.remove(os.path.abspath(filename))
                continue
            path = os.path.abspath(filename)
            sort = self.arrange(filename)
            kwags.setdefault(path, sort)

        self.logger.info("Start to combine articles....")

        for path,sort in sorted(kwags.items(), key=lambda x: x[1]):
            with open(path, "r", encoding="utf-8") as file:
                data = file.read()
                file.close()
                os.remove(path)
            with open(self.storyName+ ".txt", "a+", encoding="utf-8") as fw:
                fw.writelines(os.path.split(path)[-1].split(".")[0]+"\n"*2)
                fw.write(data)
                fw.writelines("\n"*2)
                self.logger.info("第{}章已经写入文件!".format(sort))
        else:
            fw.close()
            self.logger.info("All articles are combined to %s!"%self.storyName)
            kwags.clear()

if "__main__"==__name__:

    m = load_biquge("http://www.52bqg.com/book_86212/")

    from multiprocessing.dummy import Pool
    from multiprocessing import Pool

    try:
        with Pool(5) as pool:
            pool.map(func=m.get_save_page, iterable=m.get_page_url())
    except Exception as e:
        m.logger.error("Pool error:%s"%e)
    else:
        m.filewrite()







