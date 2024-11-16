# -- coding:utf-8 --

import time
from datetime import datetime
import ccxt
import requests
import os

import glob
import argparse

#独立程序生成target文件，说明要在哪些交易所查哪些币价，"交易对"字符串是否正确(以免到时有问题要整个程序debug）
#主程序搜索最新的target文件进行操作；或者带指定文件参数执行
#默认套利5%，或者参数指定套利比例
#套利真正要判断是买一bid和卖一ask价格，用现价是否不合适？但是买一和卖一价变动太快，是否又无实操意义？
#去中心化交易所暂定使用coingecko

#全局变量，确定是否要加代理设置
global_int_PROXY=1
global_str_win_path=".\\"
global_str_linux_path="/sys/"

path_pre=global_str_win_path

#0X的输出结果竟然没有小数位！只能用其他交易所的结果
fucking_0x_ues_former_destDecimals=0

# 获取中心化交易所的实时价格
def get_CCXT_prices(exchange, symbol):
    global global_int_PROXY
    if global_int_PROXY==0:
        exchange = getattr(ccxt, exchange)()
    else:
        #加代理，这里以v2ray为例
        exchange = getattr(ccxt, exchange)(
                                            {
                                                'proxies':{
                                                            'http':'http://127.0.0.1:10809',
                                                            'https':'http://127.0.0.1:10809',
                                                            },
                                            }
                                        )

    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']
    
def get_decentralized_prices(exchange, get_url):
    global fucking_0x_ues_former_destDecimals

    price = 0

    try:
        #0x需要秘钥访问
        if "0x" in exchange:
            headers = {
                '0x-api-key': '2d970eb2-22d1-40fc-a382-10a5567f6453',
                '0x-version': 'v2'
            }
            response = requests.get(get_url, headers=headers)
        else:
            response = requests.get(get_url)

        data = response.json()
        if "paraswap" in exchange:
            destAmount = data["priceRoute"]["destAmount"]
            destDecimals = data["priceRoute"]["destDecimals"]

            srcAmount = data["priceRoute"]["srcAmount"]
            srcDecimals = data["priceRoute"]["srcDecimals"]

            fucking_0x_ues_former_destDecimals = destDecimals
            #单价太低，例如pepe，paraswap会出现价格偏差，出现"ESTIMATED_LOSS_GREATER_THAN_MAX_IMPACT"
            #规避方法是通过10000个pepe去查价能兑换a个USDT，则每个pepe价格为a/10000
            #price = round( (int(destAmount) * (0.1 ** int(destDecimals)) ) / ( int(srcAmount) * (0.1 ** int(srcDecimals)) ), int(destDecimals))
            price = (int(destAmount) * (0.1 ** int(destDecimals))) / (int(srcAmount) * (0.1 ** int(srcDecimals)))



        elif "openocean" in exchange:
            destAmount = data["data"]["outAmount"]
            destDecimals = data["data"]["outToken"]["decimals"]
            fucking_0x_ues_former_destDecimals=destDecimals
            price = round(int(destAmount) * (0.1 ** int(destDecimals)), int(destDecimals))

        elif "0x" in exchange:
            destAmount =data["buyAmount"]
            #0x输出竟然没有小数点，借用之前别人的
            destDecimals=fucking_0x_ues_former_destDecimals
            price = round(int(destAmount) * (0.1 ** int(destDecimals)), int(destDecimals))

    except Exception as e:
        print(f"Error fetching price for {exchange} : {e}")
        price = 0

    return price


# 判断套利空间
def check_arbitrage(prices,arbitrage_filename,prices_filename,STRAT_TIME,END_TIME):
#pair,exchange,cex_dex,spot_perp,symbol,price
#0代表pair的位置,1代表exchange的位置......,-1代表价格的位置
    POS_PAIR=0
    POS_EXCHANGE=2
    POS_SPOTorPERP=4
    POS_SYMBOL=5

    arbitrage_opportunities = []
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            #price1 = prices[i][2]
            #price2 = prices[j][2]
            
            #�۸�������ĩһ��
            price1 = prices[i][-1]
            price2 = prices[j][-1]
            if abs(price1 - price2) / min(price1, price2) > 0.05:
                arbitrage_opportunities.append((prices[i], prices[j]))


    arbi_file=open(arbitrage_filename, 'a')
    arbi_file.write(STRAT_TIME + " TO " + END_TIME+'\n')
    
    if arbitrage_opportunities:
        arbi_file.write("Arbitrage opportunities found:"+'\n')
        for opp in arbitrage_opportunities:
            #print(f"{opp[0][POS_EXCHANGE]} {opp[0][POS_SPOTorPERP]} {opp[0][POS_SYMBOL]}: {opp[0][-1]} vs {opp[1][POS_EXCHANGE]} {opp[1][POS_SPOTorPERP]} {opp[1][POS_SYMBOL]} : {opp[1][-1]}")
            arbi_file.write(f'{opp[0][POS_EXCHANGE]} {opp[0][POS_SPOTorPERP]} {opp[0][POS_SYMBOL]}: {opp[0][-1]} vs {opp[1][POS_EXCHANGE]} {opp[1][POS_SPOTorPERP]} {opp[1][POS_SYMBOL]} : {opp[1][-1]}'+'\n')
    else:
        #print(f"{opp[0][POS_PAIR]}"+":"+"No arbitrage opportunities found.")
        arbi_file.write(f'{prices[0][POS_PAIR]}' + ":" + "No arbitrage opportunities found."+'\n')
    
    now=datetime.now()
    ARBITRAGE_FINISH_TIME=now.strftime("%Y%m%d%H%M%S%f")[:-3]
    #print("This Coin Arbitrage Check finished "+ARBITRAGE_FINISH_TIME)
    arbi_file.write("This Coin Arbitrage Check finished "+ARBITRAGE_FINISH_TIME+'\n')
    arbi_file.write("###"+'\n')
    arbi_file.close()

    #打印价格表，进行人工复查
	#with 语句：上下文管理器，确保在代码块执行完毕后自动关闭文件，即使在代码块中发生异常。
    with open(prices_filename, 'a') as file:
        for item in prices:
            line = ','.join(map(str, item))
            file.write(line + '\n')

        file.write('###' + '\n')

# 主程序
def main():
    global path_pre

    # 创建文件名
    target_filename_keyword = "TargetCoin"

    now=datetime.now()
    str_timestamp=now.strftime("%Y%m%d%H%M%S")
    prices_filename = path_pre+"prices_" + str_timestamp
    arbitrage_filename = path_pre+"arbitr_" + str_timestamp

    # python 本程序 -help 可以看到命令行用法
    parser = argparse.ArgumentParser(description='给出需要读取的TargetCoin文件.否则读取最新的TargetCoin文件')

    # parser.add_argument('-f', '--filename', type=str, help='JSON文件名')
    parser.add_argument('-f', '--TargetCoinFile', type=str, help='是否需要指定TargetCoin文件')

    # 解析参数
    args = parser.parse_args()
    print(f'TargetCoinFile:{args.TargetCoinFile}')

    # 命令行若传递参数，则使用相关参数；否则使用默认参数['ETH/USDT','ETH/USDC','#','PEPE/USDT','#']
    # 若是程序调试，也是使用默认参数，不用改程序
    if args.TargetCoinFile is None:
        files = glob.glob(os.path.join(path_pre, f'*{target_filename_keyword}*'))

        if not files:
            print("Quit : TargetCoin File MISSING!")
            exit(-2)

        # 找到最新的文件
        latest_file = max(files, key=os.path.getmtime)
        print({latest_file})
        #target_filename = latest_file
        target_filename = '.\TargetCoin_20241114143847'

    else:
        target_filename = args.TargetCoinFile
    print(f'target_filename : {target_filename}')

    # 创建文件后关闭
    #with open(target_filename, 'w') as file:
    #    pass
    with open(prices_filename, 'w') as file:
        pass
    with open(arbitrage_filename, 'w') as file:
        pass

    
    exchanges_pairs = []
    prices = []

    now=datetime.now()
    STRAT_TIME=now.strftime("%Y%m%d%H%M%S%f")[:-3]	

    with open(target_filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            #当一个币种情况结束，与第二个币种开始之前，用#分割
            if line and '#' not in line:
                pair,chain,exchange,cex_dex,spot_perp,symbol,get_url = line.split(',')
                exchanges_pairs.append((pair,chain,exchange,cex_dex,spot_perp,symbol,get_url))
            else:
                #开始遍历各交易所，获取该币种价格
                # prices = []
                #for pair,exchange,cex_dex,spot_perp,symbol in exchanges_pairs:
                for pair,chain,exchange,cex_dex,spot_perp,symbol,get_url in exchanges_pairs:
                    try:
                        if "CCXT" in cex_dex:
                            price = get_CCXT_prices(exchange, symbol)
                        elif "DEX" in cex_dex:
                            price = get_decentralized_prices(exchange, get_url)
            			
                        prices.append((pair,chain,exchange,cex_dex,spot_perp,symbol,get_url,price))

                    except Exception as e:
                        print(f"Error fetching price for {exchange} {pair}: {e}")

                #判断套利条件是否存在
                now=datetime.now()
                END_TIME=now.strftime("%Y%m%d%H%M%S%f")[:-3]
                arbitrage_opportunities = check_arbitrage(prices,arbitrage_filename,prices_filename,STRAT_TIME,END_TIME)

                #初始化，准备对下一个币种重复进行询价
                exchanges_pairs = []
                prices = []

                now=datetime.now()
                STRAT_TIME=now.strftime("%Y%m%d%H%M%S%f")[:-3]

if __name__ == "__main__":
    main()
