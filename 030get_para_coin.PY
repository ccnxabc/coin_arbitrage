# -- coding:utf-8 --
#使用格式python get_para_coin.PY  -f f:\\ethereum（结果保存） -chain ethereum（指定某链） -coin usd-coin wrapped-bitcoin（指定coingecko的id）
import time
import json
from datetime import datetime
import requests
import argparse
import os

parser = argparse.ArgumentParser(description='检查并更新JSON文件')

#parser.add_argument('-f', '-filename', type=str, required=True, help='JSON文件名')
parser.add_argument('-f', '--filename', type=str, help='JSON文件名')
parser.add_argument('-coin', nargs='+', help='加密货币列表')
parser.add_argument('-chain', type=str, help='公链名字')

# 解析参数
args = parser.parse_args()

# 使用解析后的参数
print(f"文件名: {args.filename}")
print(f"chain:{args.chain}")
print(f"coin:{args.coin}")

WHICH_COIN=args.chain
result_file=args.filename

#ids=['binancecoin','tether']
#ids=['usd-coin','shiba-inu','binancecoin','wrapped-steth','wrapped-bitcoin']
ids=args.coin
print(f"ids:{ids}")
#ids=['usd-coin','shiba-inu']


# 检查文件是否存在
if os.path.exists(args.filename):
    # 文件存在，# 读取原有的JSON文件
    with open(args.filename, 'r') as file:
        data = json.load(file)
    print(f"文件 {args.filename} 已存在，内容已读取。")
else:
    with (open(args.filename, 'w') as file):
        #pass
        #写一个json数据，以免后续再打开该文件读json数据为空，出错！
        coin_info ={
        "example":{
            "id": "......",
            "contract_address": "......",
            "decimals": 10
        }
        }
        json.dump(coin_info, file, indent=4)

    #创建文件后再重新打开，获取里面的json例子
    with open(args.filename, 'r') as file:
        data = json.load(file)
    print(f"文件 {args.filename} 已新建，写入了json，内容已读取。")

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