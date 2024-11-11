# -- coding:utf-8 --
#使用格式python get_para_coin.PY  -f f:\\ethereum（结果保存） -chain ethereum（指定某链） -coin usd-coin wrapped-bitcoin（指定coingecko的id）
import time
import json
from datetime import datetime
from posixpath import split

import requests
import argparse
import os
import glob

#from dask.array import zeros

#paraswap只支持以下链
#https://developers.paraswap.network/api/get-rate-for-a-token-pair-1
paraswap_chain=['1','10','56','137','250','1101','8453','42161','43114','100']
#https://docs.openocean.finance/dev/developer-resources/supported-chains
openocean_chain=['1','56','324','137','8453','59144','250','43114','42161','10','1285','1313161554','25','1666600000','2222','1088','42220','40','1101','100','204','5000','169','534352','81457','34443','30','1329','1625','solana','ont','aptos','near','starknet']
#https://0x.org/docs/developer-resources/supported-chains
zero_0x_chain=['1','42161','43114','8453','81457','56','59144','5000','34443','10','137','534352']

#https://github.com/ccxt/ccxt CCXT支持的交易所，太多，只选top10
CCXT_list=['binance','okx','bitget','bybit','whitebit','coinbase','htx','bitmart','mexc','XT','lbank','kucoin','kraken']
#CCXT_list=['binance','okx']

directory = 'f:\\'

file_chainID='chainID'
with open(directory+file_chainID, 'r') as file:
    chainID_data = json.load(file)

#keywords = ['binance-smart-chain','arbitrum-one','ethereum']
keywords = ['ethereum']

ids = ['ETH/USDT', 'ETH/USDC']

for keyword in keywords:
    files = glob.glob(os.path.join(directory, f'*{keyword}*'))

    if not files:
        continue

    # 找到最新的文件
    latest_file = max(files, key=os.path.getmtime)
    print({latest_file})

    with open(latest_file, 'r') as file:
        coin_contract_data = json.load(file)

    url_chainID=chainID_data[keyword]
    url_chainName=keyword

    #(1)输出DEX的查询URL
    for coin_pair in ids:
        out_coin= coin_pair.split("/")[0].lower()
        in_coin = coin_pair.split("/")[1].lower()

        #增加判断上述两种币，是否在相应的公链文件存在，只要一个不存在，该交易对就pass

        out_coin_contract_address=coin_contract_data[out_coin]["contract_address"]
        out_coin_decimals=coin_contract_data[out_coin]["decimals"]
        out_coin_amount=10**int(out_coin_decimals)

        in_coin_contract_address=coin_contract_data[in_coin]["contract_address"]
        in_coin_decimals=coin_contract_data[in_coin]["decimals"]

        url_openocean="https://open-api.openocean.finance/v4/"+url_chainID+"/quote?inTokenAddress="+in_coin_contract_address+"&outTokenAddress="+out_coin_contract_address+"&amount=1&gasPrice=1"
        url_paraswap="https://api.paraswap.io/prices/?srcToken="+out_coin_contract_address+"&srcDecimals="+str(out_coin_decimals)+"&destToken="+in_coin_contract_address+"&destDecimals="+str(in_coin_decimals)+"&amount="+str(out_coin_amount)+"&side=SELL&network="+url_chainID+"&version=6.2"
        url_0x="https://api.0x.org/swap/permit2/price?&chainId="+url_chainID+"&sellToken="+out_coin_contract_address+"&buyToken="+in_coin_contract_address+"&sellAmount="+str(out_coin_amount)

        if url_chainID in openocean_chain:
            print(url_openocean)
            print(f'{coin_pair},{url_chainName},openocean,DEX,SPOT,{coin_pair}-openocean,{url_openocean}')

        if url_chainID in paraswap_chain:
            print(url_paraswap)
            print(f'{coin_pair},{url_chainName},paraswap,DEX,SPOT,{coin_pair}-paraswap,{url_paraswap}')
        #需要在header加秘钥
        if url_chainID in zero_0x_chain:
            print(url_0x)
            print(f'{coin_pair},{url_chainName},0x,DEX,SPOT,{coin_pair}-0x,{url_0x}')

    # (2)输出CEX CCXT的查询
        for exchange in CCXT_list:
            #kucoin,kraken无永续合约
            if exchange=="kucoin" or exchange=="kraken":
                print(f'{coin_pair},-,{exchange},CCXT,SPOT,{coin_pair},-')
            #coinbase只使用USDC
            elif exchange=="coinbase":
                coin_pair=coin_pair.replace("USDT","USDC")
                print(f'{coin_pair},-,{exchange},CCXT,SPOT,{coin_pair},-')
            else:
                print(f'{coin_pair},-,{exchange},CCXT,SPOT,{coin_pair},-')
                print(f'{coin_pair},-,{exchange},CCXT,PERP,{coin_pair}:USDT,-')


