# -- coding:utf-8 --

import time
import json
from datetime import datetime
import requests
import argparse
import os

WHICH_COIN="ethereum"
result_file="F:\\"+WHICH_COIN

#因为coingecko网站限制，必须要延迟才能轮询
url = "https://api.coingecko.com/api/v3/coins/list"
response = requests.get(url)
data = response.json()



#ids=['binancecoin','tether']
ids=['usd-coin','shiba-inu','binancecoin','wrapped-steth','wrapped-bitcoin']
#ids=['usd-coin','shiba-inu']

# 读取原有的JSON文件
with open(result_file, 'r') as file:
    data = json.load(file)

select_coin_details = {}

for coin in ids:
    details_url = f"https://api.coingecko.com/api/v3/coins/{coin}"
    print(details_url)
    #免费的API在1秒内不能频繁申请
    time.sleep(2)
    details_response = requests.get(details_url)
    details = details_response.json()

    repeat=0

    #原文件是否有与本次coin重复的信息，如果重复后续不加入到该文件中
    for key, value in data.items():
        if value['id']==coin:
            repeat=1
            break

    #若有问题，将鼠标放在下面变量details上，可以看到exceed the Rate Limit字样
    if 'ethereum' in details['platforms'] and repeat==0:
        coin_info = {
            "id": details['id'],
            "contract_address": details['detail_platforms'][WHICH_COIN]['contract_address'],
            "decimals": details['detail_platforms'][WHICH_COIN]['decimal_place']
        }
        select_coin_details[details['symbol']] = coin_info

data.update(select_coin_details)
#{"status":{"error_code":429,"error_message":"You've exceeded the Rate Limit. Please visit https://www.coingecko.com/en/api/pricing to subscribe to our API plans for higher rate limits."}}
with open(result_file, 'w') as f:
    json.dump(data, f, indent=4)