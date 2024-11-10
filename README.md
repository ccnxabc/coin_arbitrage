USDT，USDC在coingecko只有部分链的合约地址信息；只能从其他地方补齐

USDC在各链的合约地址，来自coinmarketcap
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'xxx',
}

url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol=USDC'

response=requests.get(url2,headers=headers)
data = response.json()

 with open('e:\\890.txt', 'w') as f:
     json.dump(data, f, indent=4)
