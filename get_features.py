from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime
import urllib.request
from time import sleep,time
import gzip
from io import BytesIO
import json
import ssl
import random
import os

kinds = ['播放量','评论量','作者']

class Rank_Spider():
    def __init__(self):
        self.User_Agent = [
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
            ,
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
            ,

        ]
        self.Cookie = [
            "自己的cookie"

        ]
        self.bilibili_rank_url = {'all_rank': 'https://www.bilibili.com/ranking/all/0/0/1' ,
                     'origin_rank':'https://www.bilibili.com/ranking/origin/0/0/1',
                     'new_fan':'https://www.bilibili.com/ranking/bangumi/13/0/3',
                     'new_people':'https://www.bilibili.com/ranking/rookie/0/0/1',
                     }
    def get_head(self):
        return {
            'User-Agent': random.choice(self.User_Agent),
            'Cookie' : random.choice(self.Cookie),}

    def get_url2html(self,urls,ToPath,flag=None):
        if os.path.exists(ToPath):
            pass
        else:
            os.mkdir(ToPath)
        if flag == 1:  # 早
            ToPath = ToPath + 'morning/'
            if os.path.exists(ToPath):
                pass
            else:
                os.mkdir(ToPath)
        else:
            ToPath = ToPath + 'night/'
            if os.path.exists(ToPath):
                pass
            else:
                os.mkdir(ToPath)

        for rank_i in urls.items():
            sleep(2)
            print('抓取{}排行榜'.format(rank_i[0]))
            Res = urllib.request.Request(rank_i[1],headers=self.get_head())
            context = ssl._create_default_https_context()
            res = urllib.request.urlopen(Res,context=context)
            # print('INFO: \n',res.info())
            print('STATUS: \n',res.getcode())
            res_Str = res.read()
            # print('CONTENTS: {}\n'.format(type(res_Str.decode('utf-8'))),res_Str.decode('utf-8'))

            with open(ToPath+ rank_i[0]+ '.html','wb') as f:
                    f.write(res_Str)
            f.close()
    def run(self):
        now_data = datetime.datetime.today()
        if now_data.hour<10:
            flag = 1
        else:
            flag=0
        ToPath = r'G:\command_study\spider_project\bilibili_rank\result\day1/' + str(now_data.date()) + '/'
        self.get_url2html(self.bilibili_rank_url, ToPath,flag)
        print(str(now_data))

def write_html(path,html):
    with open(path + 'temp'+'.html', 'wb') as f:
        f.write(html)
    f.close()

def read_html(file_name):
    with open(file_name , 'rb') as f:
        html = f.read()
    f.close()
    return html

def get_video_tag(video_href,rank_spider,df):
    sleep_time = (random.random() + 1) * random.randint(1, 4) + random.randint(1, 2)
    sleep(sleep_time)
    Req = urllib.request.Request(video_href,headers=rank_spider.get_head())
    context = ssl._create_default_https_context()
    res = urllib.request.urlopen(Req,context=context)

    res_Str = res.read()
    print(res.getcode())

    buff = BytesIO(res_Str)
    f = gzip.GzipFile(fileobj=buff)
    try:
        res_Str = f.read()
    except:
        pass
    bsoup = BeautifulSoup(res_Str.decode('utf-8'), 'html.parser')

    tag = bsoup.find_all(re.compile('^li'),attrs={"class":"tag"})
    tags = []
    for tag_i in tag:
        tags.append(tag_i.a.contents)

    df['标签'] = [tags]
        # comments = bsoup.find_all(re.compile('^div'), attrs={"class": "comment-list"})
        # print(comments)
        # for comment_i in comments:
        #     print(comment_i.div.contents[1])
        #     print(comment_i.div.contents[1].div.a.contents)
    return df

def get_fans(upID,rankSpider):
    sleep_time = (random.random()+1)*random.randint(1,4)+random.randint(1,2)
    sleep(sleep_time)
    api_up = 'https://api.bilibili.com/x/relation/stat?vmid={}'.format(upID)
    headers = rankSpider.get_head()
    Req = urllib.request.Request(api_up,
                                 headers=headers)
    res = urllib.request.urlopen(Req)
    res_Str = res.read()
    jsonData = json.loads(res_Str.decode('utf-8'))

    return jsonData

def get_hot_comments_upfans(url,rankSpider,df):
    headers = rankSpider.get_head()
    av = url.split('/')[-1][2:]
    pages = 1
    json_list = []
    replyfans_list,good_list = [], []
    for page_i in range(pages):
        sleep_time = (random.random() + 1) * random.randint(1, 4) + random.randint(1, 2)
        sleep(sleep_time)
        Req = urllib.request.Request('https://api.bilibili.com/x/v2/reply?pn={}&type=1&oid={}&sort=2'.format(page_i,av),
                                     headers=headers)
        res = urllib.request.urlopen(Req)
        #获得json数据
        res_Str = res.read().decode('utf-8')
        jsonData = json.loads(res_Str)
        #从json数据里面获得 评论者id、评论者的粉丝数、评论点赞数、

        for reply_i in range(int(len(jsonData['data']['replies'])/2)):
            good_list.append(jsonData['data']['replies'][reply_i]['like'])
            reply_id = jsonData['data']['replies'][reply_i]['member']['mid']

            print('开始搜集评论up_id:',reply_id)
            reply_i_jd = get_fans(upID = reply_id,
                          rankSpider=rank_spider)

            replyfans_list.append(reply_i_jd['data']['follower'])
            print('粉丝数：',reply_i_jd['data']['follower'])
        json_list.append(jsonData)
    df['两页热评粉丝'] = [replyfans_list]
    df['两页热评点赞数'] = [good_list]
    df['两页热评json'] = [json_list]
    return df

def get_play_commend_author(html,rank_Spider):
    contents,con_dic = [],{}
    bsoup= BeautifulSoup(html.decode('utf-8'), 'html.parser')
    find_all_bank = bsoup.find_all(attrs={"class": "info"},limit=20)

    print('数量:', len(find_all_bank))
    index = 0
    for bank_i in find_all_bank:
        df = pd.DataFrame()
        index += 1
        df['排名'] = [index]
        video_href = bank_i.a['href']
        df['视频链接'] = [video_href]
        df = get_video_tag(video_href,rank_Spider,df)
        for ii, detail in enumerate(bank_i.div.contents):
            try:
                df['{}'.format(kinds[ii])] = [str(detail.contents[1])]
            except:
                df['{}'.format(kinds[ii])] = [str(detail.span.contents[1])]

                author_id = ('https:' + detail['href']).split('/')[-1]
                df['作者id'] = [author_id]
                df['作者主页'] = ['https:' + detail['href']]
                print('------------开始获得上传者和粉丝-------------')
                print('开始搜集上传up_id:', author_id)
                jsonData_author = get_fans(upID = author_id, rankSpider = rank_Spider)
                df['上传者粉丝数'] = [jsonData_author['data']['follower']]
                df['上传者json'] = [jsonData_author]
        print('------------开始获得评论者的点赞和粉丝-------------')
        df = get_hot_comments_upfans(video_href, rank_spider, df)
        df['视频题目'] = [str(bank_i.a.contents[0])]
        df['综合得分'] = [str(bank_i.find(attrs={'class': 'pts'}).div.contents[0])]
        contents.append(df)
    df = pd.concat(contents,axis=0,ignore_index=True)
    return df

if __name__ == '__main__':
    rank_spider = Rank_Spider()
    rank_spider.run()

    t1 = time()

    now_data = datetime.datetime.today()
    if now_data.hour < 12:
        flag = 'morning/'
    else:
        flag = 'night/'
    path = r'G:\command_study\spider_project\bilibili_rank\result\day1/'+ str(now_data.date()) +'/'+flag
    rank_spider = Rank_Spider()

    html = read_html(path + 'all_rank'+'.html')
    df = get_play_commend_author(html,rank_Spider=rank_spider)
    df.index = df['排名']
    df.to_csv(path + 'result.csv')
    t2 = time()
    print('时间：',(t2-t1)/60,'min')
