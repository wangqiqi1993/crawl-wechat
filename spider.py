import requests
from urllib.parse import urlencode
import re
import time
import pymysql
import random
from bs4 import BeautifulSoup
headers={
    'Cookie':'SUV=00CF4A7C279BD4225C9487C663964594; CXID=A8D5E06DB1F8FC766F5D29EEA16B4192; ad=Jex1Fyllll2tuawNlllllVhY7P1lllllJisUwkllll9lllllpv7ll5@@@@@@@@@@; SUID=22D49B274C238B0A5C98B21D00044584; IPLOC=CN1100; ABTEST=3|1555382371|v1; weixinIndexVisited=1; ld=byllllllll2tHUH0lllllVhCvLGlllllJisUwkllll9lllll9llll5@@@@@@@@@@; JSESSIONID=aaaqHKHb_zwMQ-Dia80Ow; PHPSESSID=lttcjo8lu7kon0htp6hipadeu0; sct=27; SNUID=F80D42FED9DC5DF46E89E7A1DA9182B8; ppinf=5|1556005555|1557215155|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTQlQjglODMlRTQlQjglODN8Y3J0OjEwOjE1NTYwMDU1NTV8cmVmbmljazoxODolRTQlQjglODMlRTQlQjglODN8dXNlcmlkOjQ0Om85dDJsdU9tamFaVlpyS0pyMTg4T3dnVHZCUkVAd2VpeGluLnNvaHUuY29tfA; pprdig=qJp2ategSQlXwgsi14cpe6Xa-8RiN5U_PNzMXsOl7djoBFd9YJ2CkVy0-Q_fSWASgOP6bDosfJfCXJbKT9vfHWptPb7Iw7w4IQpjTY_Iw8qmqJzo0bNSt8zFNCwkQZ_8344qD8gLEjJAFC7UcvO7gYYReTkIwCqdxy1bZsrk-gs; sgid=06-38007593-AVyibwrMVJLt7vHCHMpxC8jI; ppmdig=15560055550000002a2004dd3c32fb905c887bd3c0bd4be8',
    'Host':'weixin.sogou.com',
    'Referer': 'https://weixin.sogou.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
keyword='零售行业'
proxy_pool_url='http://api.ip.data5u.com/dynamic/get.html?order=d11275d3dace28cb2bb1ffac39975de3&sep=3'
proxy=None
max_count=5
def get_proxy():
    try:
        response=requests.get(proxy_pool_url)
        if response.status_code==200:
            return response.text
        return None
    except ConnectionError:
        return None
def get_html(url,count=1):
    print('Crawling ',url)
    print('Trying Count',count)
    global proxy
    if count>=max_count:
        print('Tried too many Counts')
        return None
    try:
        if proxy:
            proxies={
                'http':'http://'+proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers,proxies=proxies)
        else:
            response=requests.get(url,allow_redirects=False,headers=headers)
        if response.status_code==200:
            return response.text
        if response.status_code==302:
            print('302')
            proxy=get_proxy()
            if proxy:
                print('Using',proxy)
                return get_html(url,count)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occure',e.args)
        proxy=get_proxy()
        count+=1
        return get_html(url,count)
def get_index(page,keyword):
    timestamp=int(round(time.time()*1000))
    data={
        'query':keyword,
        '_sug_type_':None,
        'sut':'0',
        'lkt': '0,0,0',
        's_from': 'input',
        '_sug_':'n',
        'type': '2',
        'sst0': timestamp,
        'page': page,
        'ie': 'utf8',
        'w': '01015002',
        'dr': '1'
    }
    url='https://weixin.sogou.com/weixin?'+urlencode(data)
    html=get_html(url)
    return html
def parse_index(html):
    compile=re.compile('<div.*?class="img-box">.*?<h3>.*?<a.*?target="_blank".*?data-share="(.*?)">.*?</a>',re.S)
    results=re.findall(compile,html)
    for result in results:
        result=result.replace('amp;','')
        yield{
            'url':result
        }
def get_detail(url):
    try:
        response=requests.get(url)
        if response.status_code==200:
            return response.text
        return None
    except ConnectionError:
        return None
def parse_detail(response):
    soup = BeautifulSoup(response, 'lxml')
    try:
        title = soup.select('#activity-name')[0].get_text().strip()
        nickname = soup.select('#js_profile_qrcode > div > strong')[0].get_text().strip()
        content = soup.select('#js_content')[0].get_text().strip()
        wechat = soup.select('#js_profile_qrcode > div > p:nth-child(3) > span')[0].get_text().strip()
        date=re.findall('var.*?publish_time.*?= "(.*?)".*?;',response)[0]
        return {
                    'title':title,
                    'content':content,
                    'nickname':nickname,
                    'wechat':wechat,
                    'date':date
                }
    except:
        return{
            'title': None,
            'content': None,
            'nickname': None,
            'wechat': None,
            'date': None
        }
def insert_into_mysql(data):
    def table_exists(conn,table_name):
        sql="show tables;"
        conn.execute(sql)
        tables=[conn.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        if table_name in table_list:
            return 1
        else:
            return 0
    conn=pymysql.connect(host='localhost',user='root',password='8911980',port=3306,db='test')
    cursor=conn.cursor()
    table_name='wechat'
    if (table_exists(cursor, table_name) != 1):
        cursor.execute('create table wechat(title varchar(100),content text ,nickname varchar(50) ,wechat varchar(30),date varchar(30)) ENGINE=InnoDB DEFAULT character set utf8mb4 collate utf8mb4_general_ci;')
    title=data['title']
    content=data['content']
    nickname=data['nickname']
    wechat=data['wechat']
    date=data['date']
    try:
        cursor.execute("insert into wechat (title,content,nickname,wechat,date) values (%s,%s,%s,%s,%s)",(title,content,nickname,wechat,date))
    except:
        pass
    conn.commit()
    cursor.close()
    conn.close()
def save_to_csv(data):
    title = data['title']
    content = data['content']
    nickname = data['nickname']
    wechat = data['wechat']
    date = data['date']
    try:
        with open('lingshou.csv','a',encoding='utf-8-sig')as f:
            f.write(title+'||\t\t\t\t'+content+'||\t\t\t\t'+nickname+'||\t\t\t\t'+wechat+'||\t\t\t\t'+date)
            f.write('\n')
            f.close()
    except:
        pass
def main():
    for i in range(87,101):
        print('crawl page number:',i)
        time.sleep(2 + random.random())
        html=get_index(i, keyword)
        if html:
            article_urls=parse_index(html)
            for article_url in article_urls:
                article_url=article_url['url']
                article_html=get_detail(article_url)
                if article_html:
                    article_data=parse_detail(article_html)
                    insert_into_mysql(article_data)
                    #save_to_csv(article_data)
if __name__=='__main__':
    main()

