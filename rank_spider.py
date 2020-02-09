import urllib.request
from time import sleep
import datetime
import os
import random
import ssl

class Rank_Spider():
    def __init__(self):
        self.User_Agent = [
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
            ,
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
            ,

        ]
        self.Cookie = [
            "sid=8glpfwd9; __guid=104670726.1178218449114775800.1581048931764.8896; CURRENT_FNVAL=16; _uuid=F967601F-447D-3271-6390-5A1BA6641FAB32550infoc; buvid3=D879342A-3E6F-4277-9DBD-FFBA072DA67D53938infoc; LIVE_BUVID=AUTO9515810492969194; monitor_count=1 Host:www.bilibili.com"


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

if __name__ == '__main__':
    rank_spider = Rank_Spider()
    rank_spider.run()