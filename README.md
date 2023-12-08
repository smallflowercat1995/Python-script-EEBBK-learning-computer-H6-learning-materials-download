# Python-script-EEBBK-learning-computer-H6-learning-materials-download
Python脚本步步高学习电脑H6学习资料下载

# 目录结构：
    .
    ├── 步步高H6学习资料根据科目下载脚本.py              # Python脚本
    └── README.md                                   # 这个是说明文件   

# 起因：
    最近没找到工作，所以11月15号，从北京回到了黑龙江，唉
    在黑龙江被老家出租车司机坑了100块，没想到作为黑龙江人竟然还被老家的人坑了，真心寒
    在家里这段日子，也不知道自己要干什么很迷茫，就随意的翻腾旧物，结果找到了高中时期使用的步步高学习电脑H6
    上步步高官网竟然发现，支持H6学习资料这么多，对于熟练使用python脚本的我自然是要好好研究一下，学学英语也是不错的
    说动手就动手，开始编写脚本

# 思路：
    1.需要从步步高链接中，提取出所有科目，并根据不同科目在当前目录下创建对应的文件夹
    2.根据提取的科目名，拼接到链接中的 subjectTitle= 字段后，得到对应科目的学习资料获取的链接
    3.从拼接访问的链接中获取页数和学习资料，并存储到对应科目文件夹中，其中获取的学习资源下载链接，链接和格式不确定需要用上正则表达式
    4.下载资料的时候最好能一进度条的形式直观的显示下载进度提升交互性

# 成品代码：
    #coding:utf-8
    
    #步步高H6学习资料根据科目下载脚本
    #导入所需的库
    import requests
    from bs4 import BeautifulSoup
    import os
    import re
    import time
    import sys
    
    #定义网页的链接
    url = "http://app.eebbk.com/content/list?prodId=0cc2022340a8f735d741d4b32d3f98dd&keyword=&module=&subject=&grade=&classId=&classId1=&classId2=&classId3=&classId4=&classId5=&classId6=&gradeTitle=&subjectTitle=&order=lastTime&orderType=desc&anchor=line1&isNewEdition=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    
    #发送 HTTP 请求，获取网页的源代码
    try:
        response = requests.get(url,headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
    
    html = response.text
    
    #解析网页的 HTML 结构，提取出所有科目的名称和链接
    soup = BeautifulSoup(html, "html.parser")
    subjects = soup.select('div#subjects td.ctd a')
    
    #遍历每个科目
    for subject in subjects:
        #获取科目的名称
        name = subject.text
        #打印科目的名称
        print(name)
        #创建科目对应的文件夹，如果文件夹已经存在，则跳过
        os.makedirs(name, exist_ok=True)
        #拼接科目名到URL中
        subject_url = url.replace("subjectTitle=", "subjectTitle=" + name)
        #发送 HTTP 请求，获取网页的源代码
        try:
            response = requests.get(subject_url,headers=headers)
        except requests.exceptions.RequestException as e:
            print(e)
            continue
    
        html = response.text
        #解析网页的 HTML 结构，提取出所有下载链接的地址和总页数
        soup = BeautifulSoup(html, "html.parser")
        last_page = int(soup.select('div.pagination ul.pageul li a')[-1].text)
        print(1,"……",last_page)
        #遍历每一页
        for page in range(1, last_page + 1):
            print(page)
            #发送 HTTP 请求，获取网页的源代码
            try:
                response = requests.get(subject_url+"&page.p="+str(page),headers=headers)
            except requests.exceptions.RequestException as e:
                print(e)
                continue
    
            html = response.text
            #解析网页的 HTML 结构，提取出所有下载链接的地址
            soup = BeautifulSoup(html, "html.parser")
            downloads = soup.select('div.xz')
            #遍历每个下载链接
            for download in downloads:
                #获取下载链接的地址
                onclick = download.get('onclick')
                url = re.search(r"'(.*?)'", onclick).group(1)
                #获取文件的名称
                filename = url.split("/")[-1]
                #打印下载链接的地址和文件的名称
                print(url, filename)
                #发送 HTTP 请求，使用 stream 模式来下载文件
                try:
                    response = requests.get(url, stream=True,headers=headers)
                except requests.exceptions.RequestException as e:
                    print(e)
                    continue
    
                #打开文件，保存到对应的文件夹中
                try:
                    with open(os.path.join(name, filename), "wb") as f:
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
                    print(e)
                    continue
    
            #在请求之间添加延迟
            time.sleep(1)
# 新增
    1.添加日志功能

# 声明
本项目仅作学习交流使用，用于查找资料，学习知识，不做任何违法行为。所有资源均来自互联网，仅供大家交流学习使用，出现违法问题概不负责。 
