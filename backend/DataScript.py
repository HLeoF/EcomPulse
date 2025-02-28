import requests
import re
import execjs
import time
from urllib.parse import quote
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

def get_history_price(url_key):
    key = url_key
    shop_url = quote(key).replace('/','%2F')

    """
    构建请求头加密参数
    1. 获取网页源代码 Ticket
    2. 通过js代码内容 生成Authorization
    """
    link = f'https://tool.manmanbuy.com/historyLowest.aspx?url={shop_url}'
    headers1 = {
        'cookie':'pc_20241225_jd=1735413985050; _gid=GA1.2.1817503290.1735413985; ASP.NET_SessionId=4jvf4fbnm2unyxkta45kdxyv; Hm_lvt_01a310dc95b71311522403c3237671ae=1735414079; HMACCOUNT=ED11589968986439; Hm_lvt_85f48cee3e51cd48eaba80781b243db3=1735414082; 60014_mmbuser=AggHUgEPAwZsBFcFDg1RBAJXVQ0PVgNYDlZSAQNQXlYDBgBUUgFVVgw%3d; acw_tc=784e2caf17354240841516430e2846835de0e7ce66436e0a2c95ab22e55d65; _gat_gtag_UA_145348783_1=1; _ga_1Y4573NPRY=GS1.1.1735422180.3.1.1735424210.0.0.0; _ga=GA1.1.2131422790.1735413985; Hm_lpvt_01a310dc95b71311522403c3237671ae=1735424212; Hm_lpvt_85f48cee3e51cd48eaba80781b243db3=1735424212',
        'host':'tool.manmanbuy.com',
        'referer':'https://tool.manmanbuy.com/HistoryLowest.aspx',
        'sec-ch-ua':'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    content = requests.get(url=link, headers = headers1).text
    #提取ticket的值
    value = re.findall('id="ticket" value="(.*?)" />',content)[0]

    #读取js代码
    f = open('backend/decode.js', encoding='utf-8').read()
    #编译js代码

    js_code = execjs.compile(f)
    authorization = js_code.call('getTicket',value)

    """
    1.发送请求
    """
    #请求网址
    url = 'https://tool.manmanbuy.com/api.ashx'
    #模拟浏览器（请求头参数）
    headers = {
        'authorization':f'BasicAuth {authorization}',
        'connection':'keep-alive',
        'content-length':'161',
        'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie':'pc_20241225_jd=1735413985050; _gid=GA1.2.1817503290.1735413985; ASP.NET_SessionId=4jvf4fbnm2unyxkta45kdxyv; Hm_lvt_01a310dc95b71311522403c3237671ae=1735414079; HMACCOUNT=ED11589968986439; Hm_lvt_85f48cee3e51cd48eaba80781b243db3=1735414082; 60014_mmbuser=AggHUgEPAwZsBFcFDg1RBAJXVQ0PVgNYDlZSAQNQXlYDBgBUUgFVVgw%3d; acw_tc=784e2caf17354240841516430e2846835de0e7ce66436e0a2c95ab22e55d65; _gat_gtag_UA_145348783_1=1; _ga_1Y4573NPRY=GS1.1.1735422180.3.1.1735424218.0.0.0; _ga=GA1.1.2131422790.1735413985; Hm_lpvt_01a310dc95b71311522403c3237671ae=1735424220; Hm_lpvt_85f48cee3e51cd48eaba80781b243db3=1735424220',
        'host':'tool.manmanbuy.com',
        'origin':'https://tool.manmanbuy.com',
        'referer':f'https://tool.manmanbuy.com/historyLowest.aspx?url={shop_url}',
        'sec-ch-ua':'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with':'XMLHttpRequest',
    }

    """
    请求参数的token加密
    """

    t = int(time.time()*1000)
    shop_url = shop_url.upper()
    token = f'C5C3F201A8E8FC634D37A766A0299218KEY{shop_url}METHODGETHISTORYTRENDT{t}C5C3F201A8E8FC634D37A766A0299218'

    #MD5加密
    md5 = hashlib.md5()
    md5.update(token.encode('utf-8'))
    token = md5.hexdigest()


    data = {
        'method': 'getHistoryTrend',
        'key': key,
        't': t,
        'token': token.upper(),
    }

    json_data = requests.post(url=url,data=data,headers=headers).json()

    item_name = json_data['data']['spName']
    current_price = json_data['data']['currentPrice']
    lower_price_data = json_data['data']['lowerDate']
    lower_price = json_data['data']['lowerPrice']
    lower_price_data = lower_price_data.replace('T',' ')
    website = json_data['data']['siteName']

    datePrice_list = json_data['data']['datePrice']
    date_list = []
    price_list = []
    matches = re.findall(r"\[(\d+),([\d.]+),", datePrice_list)

    for timestamp, price in matches:
        date = datetime.utcfromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        date_list.append(date)
        price_list.append(round(float(price), 2))

    cleaned_data = {
        'item_name':item_name,
        'current_price': float(current_price),
        'lower_price_data': lower_price_data,
        'lower_price':float(lower_price),
        'website':website,
        'date_list': date_list,
        'price_list': price_list
    }
    return cleaned_data


def get_lowest_price(item_name):
    # 配置无头模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_argument("--disable-gpu")  # 如果系统是 Windows，防止错误
    chrome_options.add_argument("--no-sandbox")  # 解决某些环境中的权限问题
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决资源限制问题

    # 启动 Selenium 浏览器
    driver = webdriver.Chrome(options=chrome_options)  # 加载无头模式配置
    driver.get("https://zhekou.manmanbuy.com/")  # 打开目标网站

    # 等待页面加载
    time.sleep(2)

    # 找到搜索框并输入关键词
    search_box = driver.find_element(By.ID, "skey")  # 搜索框的 ID 是 "skey"
    search_box.send_keys(item_name)  # 输入你要搜索的关键词
    search_box.send_keys(Keys.ENTER)  # 模拟按下回车键

    # 等待页面加载结果
    time.sleep(5)

    # 获取当前页面的 URL（包含搜索的 key）
    current_url = driver.current_url
    print(f"搜索结果 URL: {current_url}")

    # 关闭浏览器
    driver.quit()
    headers2 = {
        'cookie':'60014_mmbuser=AggHUgEPAwZsBFcFDg1RBAJXVQ0PVgNYDlZSAQNQXlYDBgBUUgFVVgw%3d; Hm_lvt_85f48cee3e51cd48eaba80781b243db3=1735845432,1735929327,1735932751,1737048104; _gid=GA1.2.1125208563.1737048104; pc_20241225_jd=1737048105565; HMACCOUNT=ED11589968986439; Hm_lpvt_85f48cee3e51cd48eaba80781b243db3=1737048142; log-uid=d1e2c4388f5e4c06a6c728571868778e; ASP.NET_SessionId=tzk0kdri25lyj0sf5pae4bku; Hm_lvt_a1bdfa251db5253f12d66d6dbcada3c5=1735933092,1737048186; Hm_lpvt_a1bdfa251db5253f12d66d6dbcada3c5=1737050662; _ga=GA1.1.2131422790.1735413985; _ga_1Y4573NPRY=GS1.1.1737048104.10.1.1737051129.0.0.0',
        'host': 'zhekou.manmanbuy.com',
        'referer':'https://zhekou.manmanbuy.com/searchnew.aspx?key=https%3A%2F%2Fitem.taobao.com%2Fitem.htm%3Fid%3D744039128767%26pisk%3Dg5PoHeNbH8k5er5GNnG5CyPyv4BYobGICkdKvXnF3moX23d882l30kQS2yS7xWmqavw-v0nntyZGkGCO6zaSOjSOX1HPTwNja4JyUX7Eu2uhk4S6jStZOXSOxfyIqXGQfrjUeBJqumgn8LozYjuqy4cE84lFomun5p-zYkzVoV09U2oeTxoqWm-yTDlE0suKJH-r8Q70umgITDrELvhHTcVUGSS0qfGUUcrLi4Dobrf6TBmk6YoZkmRFbS3lfczrmBREVisSAr4RqCaxNrriWuC2Zl4YW7MbtGfoFSzgGYVB-KaxC0cqV8IkG4q8-5D4awLt4SaU1xcGdhnbOrytCf-yUVcoqAPzDe7ZavuEa0wRqIgu2yVi377pBqwUcWc-_1trv-Ugt2VCAsqgkPFShWjGggSB3dzHaBgVJSJBdYujocpW1Y_swiHE0ZbDCTMrl4IOoZvBdYujocQcod6SUqgRX%26pvid%3Dd382aea6-98a2-414d-8b9b-7cdf749f443a%26scm%3D1007.40986.420852.0%26skuId%3D5134797889715%26spm%3Da21bo.jianhua%252Fa.201876.d6.5af92a89PP8G1y%26utparam%3D%257B%2522aplus_abtest%2522%253A%2522bfa72c4798daaea8b075d14db1fb44ee%2522%257D%26xxc%3Dhome_recommend&btnSearch=%CB%D1%CB%F7',
        'sec-ch-ua':'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    content = requests.get(current_url, headers = headers2).text
    parser = BeautifulSoup(content, "html.parser")
    items = parser.find_all("li", class_="item")
    imgs = []
    names = []
    prices = []
    links = []
    malls = []

    for item in items:
        cover = item.find("div", class_="cover")
        img_src = cover.find('img')['src'] if cover else None
        
        content = item.find("div", class_="content")
        content_a = content.find('a')
        item_name = content_a.text.strip() if content_a else None
        
        highlight_a = content.find('a', class_="highlight")
        item_price = highlight_a.text.strip() if highlight_a else None
        
        link = item.find("div", class_="frinf")
        link_span = item.find("span", class_="mall")
        item_mall = link_span.text.strip() if link_span else None
        link_a = link.find('a')
        item_link = link_a['href'] if link_a else None
        
        imgs.append(img_src)
        names.append(item_name)
        prices.append(item_price)
        malls.append(item_mall)
        links.append(item_link)
        
    items_data = {
        'img_src':imgs,
        'item_name':names,
        'item_price':prices,
        'item_mall': malls,
        'item_link':links
    }

    df = pd.DataFrame(items_data)
    df = df.drop_duplicates(subset="item_name")
    item_data = df.to_json(orient='records', force_ascii=False)
    item_data
    
    return item_data