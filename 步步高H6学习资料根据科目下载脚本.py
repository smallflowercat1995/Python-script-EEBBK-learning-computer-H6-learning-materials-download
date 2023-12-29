#coding:utf-8

#步步高H6学习资料根据科目下载脚本
#导入所需的库
import requests
from bs4 import BeautifulSoup
import os
import re
import time
import sys
import logging
import threading # 导入多线程模块
import argparse # 导入命令行参数模块

# 设置日志记录
logging.basicConfig(filename='download.log', level=logging.INFO, format='%(asctime)s %(message)s')

#定义网页的链接
url = "http://app.eebbk.com/content/list?prodId=0cc2022340a8f735d741d4b32d3f98dd&keyword=&module=&subject=&grade=&classId=&classId1=&classId2=&classId3=&classId4=&classId5=&classId6=&gradeTitle=&subjectTitle=&order=lastTime&orderType=desc&anchor=line1&isNewEdition=1"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}

#创建一个Session对象，复用连接
session = requests.Session()

#发送 HTTP 请求，获取网页的源代码
def get_response(url):
    try:
        return session.get(url,headers=headers,timeout=(5,10)) # 这里我添加了timeout参数，表示连接超时和读取超时的时间，单位是秒
    except requests.exceptions.RequestException as e:
        logging.error(f'网络请求错误: {e}')
        exit()

#解析网页的 HTML 结构，提取出所有科目的名称和链接
def get_soup(html):
    return BeautifulSoup(html, "html.parser")

#恢复下载文件，根据文件的字节位置
def resume_download(fileurl, resume_byte_pos):
    resume_header = {'Range': 'bytes=%d-' % resume_byte_pos}
    return session.get(fileurl, headers=resume_header, stream=True, verify=False, allow_redirects=True, timeout=(5,10)) # 这里我也添加了timeout参数

#遍历每个科目
'''
    [英语, 语文, 数学, 文数, 理数, 奥语, 奥数, 奥英, 物理, 化学, 生物, 政治, 历史, 地理, 文综, 理综, 科学, 常识, 艺术, 社会, 健康]
'''
def iterate_subjects(subjects, url):
    #list_test=["英语", "语文", "数学", "文数", "理数", "奥语", "奥数", "奥英", "物理", "化学", "生物", "政治", "历史", "地理", "文综", "理综", "科学", "常识", "艺术", "社会", "健康"]
    #print(type(list_test),list_test)
    print(subjects)
    for subject in subjects:
        #获取科目的名称
        name = subject.text
        #打印科目的名称，可以手动指定学科
        #name = list_test[14] # 这里你把name赋值为文综，但是你没有用到这个变量，而是继续遍历subjects，这可能会导致你下载的不是你想要的科目。如果你只想下载文综，你可以直接break出循环，或者用if语句判断name是否等于文综。
        print(name)
        #创建科目对应的文件夹，如果文件夹已经存在，则跳过
        os.makedirs(name, exist_ok=True)
        #拼接科目名到URL中
        subject_url = url.replace("subjectTitle=", "subjectTitle=" + name) # 这里我把这一行代码放到了for循环里面，这样每次循环时，subject_url都会根据不同的科目名进行更新，然后你就可以下载所有科目的文件了。
        #创建一个线程，执行下载科目的函数
        thread = threading.Thread(target=download_subject, args=(subject_url, name)) # 使用多线程模块，创建一个线程对象，传入下载科目的函数和参数
        thread.start() # 启动线程

#下载一个科目的所有文件
def download_subject(subject_url, name):
    #发送 HTTP 请求，获取网页的源代码
    response = get_response(subject_url)
    html = response.text
    #解析网页的 HTML 结构，提取出所有下载链接的地址和总页数
    soup = get_soup(html)
    #获取分页的元素列表
    pages = soup.select('div.pagination ul.pageul li a')
    #判断列表是否为空
    if pages:
        #如果不为空，取出最后一个元素的文本，转换成整数
        last_page = int(pages[-1].text)
    else:
        #如果为空，说明只有一页，直接赋值为1
        last_page = 1
    print(1,"……",last_page)
    #遍历每一页
    for page in range(1, last_page + 1):
        item_count=0
        #发送 HTTP 请求，获取网页的源代码
        response = get_response(subject_url+"&page.p="+str(page))
        html = response.text
        #解析网页的 HTML 结构，提取出所有下载链接的地址
        soup = get_soup(html)
        downloads = soup.select('div.xz')
        #遍历每个下载链接
        for download in downloads:
            item_count+=1
            #获取下载链接的地址
            onclick = download.get('onclick')
            url = re.search(r"'(.*?)'", onclick).group(1)
            #获取文件的名称
            filename = url.split("/")[-1]
            #判断文件是否是你不想下载的文件
            if filename == "学习电脑_H6_V1.11_一卡系统恢复.zip": # 这里我添加了一个if语句，如果文件名等于你不想下载的文件名，就跳过这个文件，继续下一个文件。
                logging.info(f'文件不需要下载，跳过: {url}, {filename}')
                print(f'文件不需要下载，跳过: {url}, {filename}')
                continue
            file_path = os.path.join(name, filename) # 使用os.path.join()函数，拼接文件的路径
            #打印下载链接的地址和文件的名称
            print(page, item_count, url, file_path)
            #判断文件是否已经存在
            if os.path.exists(file_path):
                #获取文件的大小
                file_size = os.path.getsize(file_path)
                #发送 HTTP 请求，获取文件的总大小
                try:
                    response = requests.head(url, headers=headers, timeout=(5,10)) # 这里我也添加了timeout参数
                except requests.exceptions.RequestException as e:
                    logging.error(f'获取文件大小失败: {url}, {filename}')
                    continue
                total_length = int(response.headers.get('content-length'))
                #判断文件大小是否与要下载的网络文件大小一致
                if file_size == total_length:
                    #如果一致，则跳过
                    logging.info(f'文件已存在，跳过下载: {url}, {filename}')
                    continue
                else:
                    #如果不一致，则断点续传
                    logging.info(f'文件不完整，继续下载: {url}, {filename}')
                    #发送 HTTP 请求，使用 stream 模式来下载文件
                    try:
                        response = resume_download(url, file_size)
                    except requests.exceptions.RequestException as e:
                        logging.error(f'下载失败: {url}, {filename}')
                        continue
                    #打开文件，追加到对应的文件夹中
                    try:
                        with open(file_path, "ab") as f: # 使用with语句，自动管理文件的打开和关闭
                            #初始化已下载的大小
                            downloaded = file_size
                            #遍历每个数据块
                            for chunk in response.iter_content(chunk_size=1024):
                                #如果数据块不为空，写入文件
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    #打印下载进度
                                    done = int(50 * downloaded / total_length)
                                    sys.stdout.write("\r%sMB/%sMB [%s%s] %d%%" % (downloaded/(1024*1024), total_length/(1024*1024), '#' * done, '.' * (50-done), done * 2))
                                    sys.stdout.flush()
                            sys.stdout.write('\n')
                    except IOError as e:
                        logging.error(f'文件操作错误: {e}')
                        # 如果发生错误，删除文件
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        continue
            else:
                #如果文件不存在，则直接创建文件下载
                logging.info(f'文件不存在，开始下载: {url}, {filename}')
                #发送 HTTP 请求，使用 stream 模式来下载文件
                try:
                    response = get_response(url)
                except requests.exceptions.RequestException as e:
                    logging.error(f'下载失败: {url}, {filename}')
                    continue
                #打开文件，保存到对应的文件夹中
                try:
                    with open(file_path, "wb") as f:
                        #获取文件的总大小
                        total_length = int(response.headers.get('content-length'))
                        #初始化已下载的大小
                        downloaded = 0
                        #遍历每个数据块
                        for chunk in response.iter_content(chunk_size=1024):
                            #如果数据块不为空，写入文件
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                #打印下载进度
                                done = int(50 * downloaded / total_length)
                                sys.stdout.write("\r%sMB/%sMB [%s%s] %d%%" % (downloaded/(1024*1024), total_length/(1024*1024), '#' * done, '.' * (50-done), done * 2))
                                sys.stdout.flush()
                        sys.stdout.write('\n')
                except IOError as e:
                    logging.error(f'文件操作错误: {e}')
                    # 如果发生错误，删除文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    continue

        #在请求之间添加延迟
        time.sleep(1)

#启动
if "__main__"==__name__:
    response = get_response(url)
    html = response.text
    soup = get_soup(html)
    subjects = soup.select('div#subjects td.ctd a')
    iterate_subjects(subjects, url)
