import requests
from bs4 import BeautifulSoup
import json
import urllib
import re
from urllib import parse,request
import time 
from lxml import etree
#####################################################
keyword = 'python'#######关键词(可以修改)
flag = 0 
page = 0###################第几页  ###可以循环N页（奇数）
curbook=0#多少本书
book = 100#循环100本(可以修改)
list_jd = [[]for i in range (book)]
while(flag==0):
    page=page*2+1
    print('第'+str(page)+'个页面')
    #############查找前30个商品的data-pid#############################################
    params = {'keyword':keyword,'enc':'utf-8','qrst':1,'rt':1,'stop':1,'vt':2,'page':page,'click':0}
    data = parse.urlencode(params)
    opener = request.urlopen("https://search.jd.com/Search?"+data)
    print("搜索页面:https://search.jd.com/Search?"+data)
    content = opener.read()
    opener.close()
    soup = BeautifulSoup(content,"html.parser")
    goods_info = soup.select(".gl-item")
    pid = []
    for good_info in goods_info:
        pid.append(good_info.attrs['data-sku'])
    print('当前页前30个书目',pid)###调试用语句
    ####################设法获得当前页后30个商品的data-pid################
    other_url = "https://search.jd.com/s_new.php?keyword="+keyword+"&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq="+keyword+"&page="+str(page+1)+"&scrolling=y&log_id={}&tpl=2_M&show_items={}"###s需要修正，往往不定值
    linux_sec = str(time.time())[:-2]#时间戳去掉后两位
    other_url = other_url.format(linux_sec, ','.join(pid))#构造后半部分网页，有三处要除以一个page+1，一处是log_id为时间戳去掉后两位，最后的一堆列表是前半部分解析的data-pid构成的
    print('other_url',other_url)###调试用语句
    headers = {
        #refer必须带，表示又前一网页跳转过来
        'referer': "https://search.jd.com/Search?{}".format(str(page))
    }
    r = requests.get(url = other_url, headers=headers,verify = False,timeout=15)
    r.encoding = r.apparent_encoding
    response = r.text
    for i in range(30):
        pida = response.split('data-sku=')[i*2+1].split('\"')[1]##########注自己写的（要验证）
        pid.append(pida) ###把获得的后30个书目添加到pid数组
        
    print('当前页前30+后30一共60个书目',pid)###调试用语句
   
    
    #############根据商品的PID查找所有链接################################
    ################每个商品的商品名，价格，评论###########################
    for good_info in pid:
        curbook+=1
        if(curbook>book):
            flag=1
            break
        print('第'+str(curbook)+'本书')
        ###########修改的地方是下面一行，爬取 商品名，价格，评论########
        urll = 'https://item.jd.com/'+str(good_info)+'.html'#https://item.jd.com/12394587.html'#######这个地址可以变，其他不要改,目前能运行 item开头的网址
        ##########输出名称########
        print('网址链接:',urll)
        html_ = requests.get(urll).text
        soup_page = BeautifulSoup(html_,'html5lib')
        soup_page.prettify()
        name= soup_page.find('div',class_="sku-name").strings        
        for str_ in name:
            print('书名:',str_.strip())
            list_jd[curbook-1].append('书名:'+str_.strip())
        #########输出价格#########
        sku = urll.split('/')[-1].strip(".html") 
        price_url = "https://p.3.cn/prices/mgets?skuIds=J_" + sku # cannot change
        response = urllib.request.urlopen(price_url) 
        content = response.read() 
        content = content.decode("utf-8")
        result = json.loads(content) 
        record = result[0] 
        price = record['p']
        print('价格:',price)
        list_jd[curbook-1].append('价格:'+price)
        #########输出评论#########
        ########可以修改数值range(N)########
        ########sortType是评论类别，好评差评，可以修改数值###########
        ########page是评论在第几页########################
        ########score
        ########pageSize
        ########isShadowSku
        ########fold
        m=0 
        for pagenum in range(100):####循环评论页数可以适当扩大(可以修改)
            comment_url='https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv17182&productId='+urll.split('/')[-1].split('.')[0]+\
            '&score=0&sortType=0&page='+str(pagenum+1)+'&pageSize=10&isShadowSku=0&fold=1' #####此处，可以循环爬取page 
            pagere=urllib.request.urlopen(comment_url)
            html=pagere.read().decode("gbk")
            html=html.replace('fetchJSON_comment98vv17182(','')
            html=html.replace(');','')
            try:            ####处理评论数为0的异常
                comment=json.loads(html)
            except:
                continue ####处理评论数为0的异常
            for k in comment["comments"]: 
                m=m+1
                list_jd[curbook-1].append('第'+str(m)+'个评论:'+k["content"])
                print ('第'+str(m)+'个评论:'+k["content"])
#    print(list_jd)
print(list_jd)