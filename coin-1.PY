# -- coding:utf-8 --

import time
from datetime import datetime
import ccxt
import requests

#独立程序生成target文件，说明要在哪些交易所查哪些币价，"交易对"字符串是否正确(以免到时有问题要整个程序debug）
#主程序搜索最新的target文件进行操作；或者带指定文件参数执行
#默认套利5%，或者参数指定套利比例
#套利真正要判断是买一bid和卖一ask价格，用现价是否不合适？但是买一和卖一价变动太快，是否又无实操意义？
#去中心化交易所暂定使用coingecko

#全局变量，确定是否要加代理设置
global_int_PROXY=1
global_str_win_path="F:\\"
global_str_linux_path="/sys/"

path_pre=global_str_win_path

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
    
def get_decentralized_prices(exchange, symbol):
    price = 0

    try:
        response = requests.get(symbol)
        data = response.json()
        if "paraswap" in exchange:
            destAmount = data["priceRoute"]["destAmount"]
            destDecimals = data["priceRoute"]["destDecimals"]

        elif "openocean" in exchange:
            destAmount = data["data"]["outAmount"]
            destDecimals = data["data"]["outToken"]["decimals"]

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
    POS_EXCHANGE=1
    POS_SPOTorPERP=3
    POS_SYMBOL=4

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

    now=datetime.now()
    str_timestamp=now.strftime("%Y%m%d%H%M%S")
		
    # 创建文件名
    target_filename = path_pre+"target_" + str_timestamp
    prices_filename = path_pre+"prices_" + str_timestamp
    arbitrage_filename = path_pre+"arbitr_" + str_timestamp
		
    ################
    # #测试后删除
    #################
    target_filename=path_pre+"123.txt"
		
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
            #当一个币种情况结束，与第二个币种开始之前，用###分割
            if line and '###' not in line:
                pair,exchange,cex_dex,spot_perp,symbol = line.split(',')
                exchanges_pairs.append((pair,exchange,cex_dex,spot_perp,symbol))
            else:
                #开始遍历各交易所，获取该币种价格
                # prices = []
                #for pair,exchange,cex_dex,spot_perp,symbol in exchanges_pairs:
                for pair,exchange,cex_dex,spot_perp,symbol in exchanges_pairs:
                    try:
                        if "CCXT" in cex_dex:
                            price = get_CCXT_prices(exchange, symbol)
                        elif "DEX" in cex_dex:
                            price = get_decentralized_prices(exchange, symbol)
            			
                        prices.append((pair,exchange,cex_dex,spot_perp,symbol, price))

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
