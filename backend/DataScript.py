import requests
import re
import execjs
import time
from urllib.parse import quote
import hashlib
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

#配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_itemPrice_data(url):
    key = url
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
        price_list.append(float(price))

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


@app.route('/catchUrl', methods=['POST'])
def catchWeb_URL():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error':'URL IS NOT REQUIRED'}), 400
        
        url = data['url']
        logger.info(f'URL Catched: {url}')
        
        #验证URL的格式
        if not url.startswith(('http://','https://')):
            return jsonify({'error':'Invalid URL format'}), 400
        try:
            item_price_data = get_itemPrice_data(url)
            return jsonify(item_price_data)
        except Exception as e:
            return jsonify({'error':str(e)}), 500
        
    except Exception as e:
        logger.error(f"ERROR in catchWeb_URL: str{e}"), 500
        return jsonify({'error':str(e)}), 500

if __name__ == '__main__':
    app.run(port=2233)