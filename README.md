# python_crawl
A crawl programmed using python2.7 to collect comments on specific books from the website of JD.COM, finished in May 2018.
Directly run the .ipynb file to display outputs. 




```python
import requests  
from bs4 import BeautifulSoup #
import json
import urllib
import time   
import re
import urlparse
import urllib2

#第一步，构建书籍的id列表

keyword = 'python' #关键词(可以修改)
page = 0###################第几页  ###可以循环N页（奇数）
book_num = 100 #一共100本书
list_jd = [[] for i in range(book_num)]

#首先抓取第1页前30个结果的id
params = {'keyword':keyword,'enc':'utf-8','qrst':1,'rt':1,'stop':1,'vt':2,'page':page,'click':0}
data = urllib.urlencode(params)
opener = urllib2.urlopen("https://search.jd.com/Search?"+data)
content = opener.read()
opener.close()
soup = BeautifulSoup(content,"html.parser")
goods_info = soup.select(".gl-item")
pid = []
for good_info in goods_info:
    pid.append(good_info.attrs['data-sku'])

#再抓取第1页后30个结果的id
page=page*2+1
other_url = "https://search.jd.com/s_new.php?keyword="+keyword+"&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq="+keyword+"&page="+str(page+1)+"&scrolling=y&log_id={}&tpl=2_M&show_items={}"###s需要修正，往往不定值
linux_sec = str(time.time())[:-2]#时间戳去掉后两位
other_url = other_url.format(linux_sec, ','.join(pid))#构造后半部分网页，有三处要除以一个page+1，一处是log_id为时间戳去掉后两位，最后的一堆列表是前半部分解析的data-pid构成的
headers = {
    'referer': "https://search.jd.com/Search?{}".format(str(page))
}
r = requests.get(url = other_url, headers=headers,verify = False,timeout=15)
r.encoding = r.apparent_encoding
response = r.text
for i in range(30):
    pida = response.split('data-sku=')[i*2+1].split('\"')[1]
    pid.append(pida)
    
#抓取第2页前30个结果的id
page = page*2+1
params = {'keyword':keyword,'enc':'utf-8','qrst':1,'rt':1,'stop':1,'vt':2,'page':page,'click':0}
data = urllib.urlencode(params)
opener = urllib2.urlopen("https://search.jd.com/Search?"+data)
content = opener.read()
opener.close()
soup = BeautifulSoup(content,"html.parser")
goods_info = soup.select(".gl-item")
for good_info in goods_info:
    pid.append(good_info.attrs['data-sku'])

#抓取第2页后30个结果的id
other_url = "https://search.jd.com/s_new.php?keyword="+keyword+"&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq="+keyword+"&page="+str(page+1)+"&scrolling=y&log_id={}&tpl=2_M&show_items={}"###s需要修正，往往不定值
linux_sec = str(time.time())[:-2]
other_url = other_url.format(linux_sec, ','.join(pid))
headers = {
    'referer': "https://search.jd.com/Search?{}".format(str(page))
}
r = requests.get(url = other_url, headers=headers,verify = False,timeout=15)
r.encoding = r.apparent_encoding
response = r.text
for i in range(30):
    pida = response.split('data-sku=')[i*2+1].split('\"')[1]
    pid.append(pida)

#print pid    
#发现id存在重复，进行去重,同时保证id顺序按照搜索结果排序
pid_ =list(set(pid))
pid_.sort(key=pid.index)
print (pid_,len(pid_))

```


    ---------------------------------------------------------------------------
    
    ModuleNotFoundError                       Traceback (most recent call last)
    
    <ipython-input-5-8039dd5b9e36> in <module>()
          5 import time
          6 import re
    ----> 7 import urlparse
          8 import urllib2
          9 


    ModuleNotFoundError: No module named 'urlparse'



```python
import requests  #
from bs4 import BeautifulSoup #
import json
import urllib
import numpy as np
import random

book_num = 100 #一共100本书
list_jd = [[] for i in range(book_num)]
t = 3 #被截断后休息的最长时间
test = True #显示测试过程
count = 0 #计数
for i in range(book_num):
    count +=1
    
    if test:
        print ('Getting book ' + str(count) + ' , with ' + str(book_num) + ' books in total') #显示抓取进度
    
    sku = int(pid_[i])
    url = 'https://item.jd.com/' + bytes(sku) + '.html'  
    html_ = requests.get(url).content
    soup_page = BeautifulSoup(html_,'html5lib') 
    books_name = soup_page.find('div',class_="sku-name").strings
    for str_ in books_name:
        name_ = str_.strip()
    #print name_
    list_jd[i].append(name_)

    price_url = "https://p.3.cn/prices/mgets?skuIds=J_" + bytes(sku)
    response = urllib.urlopen(price_url) 
    content = response.read() 
    content = content.decode("utf-8")
    result = json.loads(content) 
    record = result[0] 
    price=record['p'] 
    list_jd[i].append(price)

    comment_ = []
    for j in range(1,100): #京东商品页面最多显示100页评论
        url_comm = 'https://sclub.jd.com/comment/productPageComments.action?productId=' + bytes(sku) + '&score=0&sortType=5&'+'page='+str(j)+'&pageSize=10&isShadowSku=0&rid=0&fold=1'
        
        try:#异常抛出
            html_comm=requests.get(url_comm).text
            if html_comm:
                json_html_comm=json.loads(html_comm)
                comment_list=json_html_comm['comments']
            else:
                break
        except:#被截断访问后休眠1~3秒后继续访问
            time.sleep(random.randint(1,t))
            html_comm=requests.get(url_comm).text
            if html_comm:
                json_html_comm=json.loads(html_comm)
                ocomment_list=json_html_comm['comments']
            else:
                break
        for se in comment_list:
            comment_.append(se['content'])        
        #剔除重复的评论,保留按页面展示结果的排序
        comment_1 = list(set(comment_))
        comment_1.sort(key=comment_.index)
        
    book_comment= '####'.join(comment_1)
    list_jd[i].append(book_comment)

print (list_jd)

```

    Getting book 1 , with 100 books in total



    ---------------------------------------------------------------------------
    
    NameError                                 Traceback (most recent call last)
    
    <ipython-input-4-fafaff77c339> in <module>()
         17         print ('Getting book ' + str(count) + ' , with ' + str(book_num) + ' books in total') #显示抓取进度
         18 
    ---> 19     sku = int(pid_[i])
         20     url = 'https://item.jd.com/' + bytes(sku) + '.html'
         21     html_ = requests.get(url).content


    NameError: name 'pid_' is not defined



```python
import pandas as pd
columns=['书名','售价','评论']
books = pd.DataFrame(list_jd,columns=columns)
books.to_csv("Jingdong.csv",index=False,encoding="utf-8")
print books
```

                                                       书名      售价  \
    0                            Python编程从零基础到项目实战（微课视频版）   66.20   
    1                                     Python编程 从入门到实践   72.70   
    2                                     零基础学Python（全彩版）   57.90   
    3                                 Python从入门到项目实践（全彩版）   72.40   
    4                                                       82.90   
    5                                     Python基础教程（第3版）   80.90   
    6                                                       95.80   
    7                                      Python编程从入门到精通   66.20   
    8                                        笨办法学Python 3   49.40   
    9                                 Python编程（第4版 套装上下册）  157.00   
    10                              Python编程快速上手 让繁琐工作自动化   57.80   
    11                                       Python神经网络编程   57.80   
    12                                   Python 3网络爬虫开发实战   80.90   
    13                                       Python从菜鸟到高手  106.10   
    14                                       Python从小白到大牛   72.00   
    15                                基于Python的大数据分析基础及实战   57.20   
    16                                          流畅的Python  113.60   
    17                                    Python数据分析与挖掘实战   55.50   
    18                                    数据结构 Python语言描述   57.80   
    19                                         Python深度学习   97.20   
    20                                 Python零基础入门学习-水木书荟   35.40   
    21                   2本 Python编程从入门到实践+Python核心编程 第3版  129.80   
    22                           O'Reilly：Python学习手册（第4版）   95.80   
    23                             Head First Python（第二版）   93.70   
    24                                        Python 3标准库  157.20   
    25                            Python Cookbook（第3版）中文版   90.50   
    26                                                      71.60   
    27                                         Python算法教程   57.80   
    28                                       Python自然语言处理   74.50   
    29                            Python绝技：运用Python成为顶级黑客   67.90   
    ..                                                ...     ...   
    70                                         Python数据处理   78.00   
    71                                Python自动化运维：技术与最佳实践   53.60   
    72                                 从零开始学Python数据分析与挖掘   63.20   
    73                                跟老齐学Python：Django实战   59.30   
    74                                    Python袖珍指南（第5版）   29.10   
    75                               Python数据科学：技术详解与商业实践   76.90   
    76                       Selenium 2自动化测试实战 基于Python语言   50.70   
    77                 Flask Web开发 基于Python的Web应用开发实战 第2版   54.40   
    78                  Python+Spark 2.0+Hadoop机器学习与大数据实战   79.20   
    79                             自动化平台测试开发：Python测试开发实战   59.30   
    80                                                      61.30   
    81      深度学习系列：基础教程+Python+Tensorflow+Theano（京东套装共4册）  202.20   
    82                                    从零开始学Python网络爬虫   45.80   
    83               Python学习手册（原书第5版） 计算机与互联网 书籍|8053406  145.64   
    84                                         Python测试之道   50.10   
    85                                     Python高级编程 第2版   74.50   
    86                                    趣学Python：教孩子学编程   49.40   
    87                                         Python机器学习   61.30   
    88                            Python从入门到精通（软件开发视频大讲堂）   63.80   
    89                                         Python文本分析   62.30   
    90                                     Python机器学习实践指南   57.80   
    91                              利用Python进行数据分析（原书第2版）   79.70   
    92  正版包邮 Python编程 从入门到实践 基本教程到完整项目开发爬虫学习数据分析处理 语言程...   56.00   
    93                                 Python参考手册 第4版 修订版   74.50   
    94                                Python地理空间分析指南（第2版）   66.20   
    95                                       Python游戏编程入门   41.00   
    96          PySpark实战指南：利用Python和Spark构建数据密集型应用并规模化部署   38.10   
    97                                                      41.00   
    98                                        Python高性能编程   66.20   
    99                                   Python数据分析与数据化运营   76.90   
    
                                                       评论  
    0   已经开始看了哦，活到老学到老，书是最好的伙伴####一直在京东买，没什么好说的。####正在...  
    1   我们这群人，苦没有真正苦过，爱没有用力爱过。每天受着信息大潮的冲击，三观未定又备受曲折。贫穷...  
    2   买了备着，优惠价确实很实惠，有时间再学习下最新的语言####这本书适合初学者，内容很详细，质...  
    3   书的排班整洁，完全是按初学者的角度来编辑这本书的，很好，附送的光盘，对于我来说非常有用，毕竟...  
    4   终于收到我需要的宝贝了，东西很好，价美物廉，谢谢掌柜的！说实在，这是我购物来让我最满意的一次...  
    5   和此卖家交流，与卖家您交流，我只想说，老板你实在是太好了。 你的高尚情操太让人感动了。本人对...  
    6   一本好书，一本手册，一个好工具！支持python3.6####终于收到我需要的宝贝了，东西很...  
    7   一本好书，一本手册，一个好工具！支持python3.6####终于收到我需要的宝贝了，东西很...  
    8   一本好书，一本手册，一个好工具！支持python3.6####终于收到我需要的宝贝了，东西很...  
    9   一本好书，一本手册，一个好工具！支持python3.6####终于收到我需要的宝贝了，东西很...  
    10  不错哦，活动时候买的，偶尔看看，买书如山倒&hellip;不知道啥时候能看完&hellip;...  
    11  原来同事出的书，逻辑合理，彩色打印，图文结合，纸张质量也不错####快递很快，纸张不错，彩页...  
    12  书很好，是正版，京东购物很方便，比书店便宜，活动买，更合算，物流很快。####商品质量符合图...  
    13  机器学习是计算机科学与人工智能的重要分支领域. 本书作为该领域的入门教材，在内容上尽可能涵盖...  
    14  机器学习是计算机科学与人工智能的重要分支领域. 本书作为该领域的入门教材，在内容上尽可能涵盖...  
    15  机器学习是计算机科学与人工智能的重要分支领域. 本书作为该领域的入门教材，在内容上尽可能涵盖...  
    16  和此卖家交流，与卖家您交流，我只想说，老板你实在是太好了。 你的高尚情操太让人感动了。本人对...  
    17  还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好还好...  
    18  吾消费京东商城数年，深知各产品琳琅满目。然，唯此宝物与众皆不同，为出淤泥之清莲。使吾为之动容...  
    19  还没开始看，包装但是没问题，看过后再来评价！\n书本身是本好书，刚出不久，好评不断！适合初学...  
    20  机器学习是计算机科学与人工智能的重要分支领域. 本书作为该领域的入门教材，在内容上尽可能涵盖...  
    21  书很好，包装很严实，书的质量也很好####源代码和答案要在图灵社区下载####书很好很新，内...  
    22  书很好，包装很严实，书的质量也很好####源代码和答案要在图灵社区下载####书很好很新，内...  
    23  Head First Python（第二版） 书不错####很不错，非常值得买，物流非常快，...  
    24  非常厚实的一本学习手册，值得啃。####书质量不错，发货速度很快，趁着京东价格打折，赶快买一...  
    25  双11，有好券就买了几本python书####好厚的一本书，内容很不错，值得####Pyth...  
    26  京东大品牌，购物很放心，下单方便，工作人员送货及时，书很不错，是正版，搞活动的时候囤货更划算...  
    27  和此卖家交流，与卖家您交流，我只想说，老板你实在是太好了。 你的高尚情操太让人感动了。本人对...  
    28  和此卖家交流，与卖家您交流，我只想说，老板你实在是太好了。 你的高尚情操太让人感动了。本人对...  
    29  包装完整，是新书，一次买了好多书，内容还没有仔细研究，粗略的看了一下还不错！####比较基础...  
    ..                                                ...  
    70  都是比较基础的入门应用，对入门有帮助。####不错的书籍，就是有点贵，物流还不错，有点小挤压...  
    71  都是比较基础的入门应用，对入门有帮助。####不错的书籍，就是有点贵，物流还不错，有点小挤压...  
    72                                                     
    73  这个我一直都想要了，感觉也是学完基础以后要学的，但也算是基础吧，具体应用还要学做项目####...  
    74  书基本上都是京东买的 非常实惠 性价比很高####内容很多都有涉猎，注意我的用词是涉猎，所以...  
    75  书基本上都是京东买的 非常实惠 性价比很高####内容很多都有涉猎，注意我的用词是涉猎，所以...  
    76  没毛病，都是京东上买的。快递又快书又完好####这个也是入门级的书，适合我这种小白####图...  
    77  正品质量不错，纸张坚挺文字清晰####此用户未填写评价内容####GVuv发一份v丰富uu发...  
    78  挺详细的，好好学习学习，好评！####书很不错，机器学习，计算机视觉，书很不错，值得一看，深...  
    79  纸质不错，内容还挺全，刚开始看，希望能学到更多知识～到时再追加结果####很喜欢，该书写的风...  
    80  我的评论只有一个字，那就是：好。如果非要两个字的话，我要说：很好。如果你还觉得不够，我说好得...  
    81  没有理论说明，代码多####质量还不错，快递速度快。####等看完再过来评价！京东的服务是挺...  
    82  很实用吧，有的地方会少写引用，安装scrapy的地方也没说全，很多还是得自己去百度，总体不错...  
    83                                                     
    84  好书，推荐，Python测试之道，提升自己####收到书了，很不错，包装很完整，####买来...  
    85  非常不错，质量很棒，字体很清晰，价格合理，值得购买，很满意的一次购物####我为什么喜欢在京...  
    86  京东快递给力，刚买上，看看再做具体评价，书是正品哈。####哈哈哈哈哈哈哈哈哈哈哈很基础很有...  
    87  一口气买了十几本py书，趁着双11，优惠力度很大。够学半年一载的了。粗翻目录，有新鲜知识点。...  
    88                                                     
    89  不知道是不是语言学本身就晦涩难懂的缘故，还是翻译得不好，看着很费力，另外，书中出现了部分低级...  
    90  好好学习机器学习，前途无量。####学习现在热门的知识用。书很新，塑封了####纸质不错 快...  
    91  还行吧，看了头几页对初学者可能有点难度####这本书还没看呢，不过应该是比较好的一本书，我也...  
    92                                                     
    93  满减优惠，专业必备，质好经典，物流速达，一如继往的好，非常满意，满分！！！####相信对我会...  
    94  老婆说，要是有彩图就好了####现阶段很需要的工具书。看目录感觉应该很有用。####学习学习...  
    95  内容还行，要抽时间学习####也是为了了解一下下游戏这行####屯了一堆书，看完要好久###...  
    96  一口气买了十几本py书，趁着双11，优惠力度很大。够学半年一载的了。粗翻目录，有新鲜知识点。...  
    97  好书，我最近正在学，正需要这种好书。####有一定的内容，主讲matplotlib，和mat...  
    98  还剩好多好多好多比我大北京现代结合虾兵蟹将都拿不到八点半下班的鸡蛋牛奶等不到八点半下班的鸡蛋...  
    99  很好，很方便，很喜欢。很喜欢在这里买东西，但是20个字也太难了。####快递很给力，当天买当...  
    
    [100 rows x 3 columns]

