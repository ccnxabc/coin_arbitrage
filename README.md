（1）通过congecko，看下有哪些热门交易币种

（2）点击上述币种，在左侧Info，获取该币种在coingecko的唯一区别id。例如USDC在coingecko的id是usd-coin。通过030get_para_coin.PY生成ethereum、binance-smart-chain等以某链命名的文件（这些链命名也是以coingecko为准，例如币安的链叫binance-smart-chain，而不是BSC），文件里面是获取相应的币在某链上的合约地址，主要用于去中心化交易所DEX进行查价。
python 030get_para_coin.PY  -f f:\\ethereum（结果保存） -chain ethereum（指定某链） -coin usd-coin wrapped-bitcoin（指定coingecko的id）
-f f:\\ethereum（结果保存在文件ethereum） 
-chain ethereum（指定某链） 
-coin usd-coin wrapped-bitcoin（指定coingecko的id，例如USDC在coingecko的id是usd-coin）

token和合约地址的关系，是一个体力劳动累积的过程，并且某些币竟然在coingecko查不到，例如USDT在congecko竟然没有BSC链！这就只能自己手工加上去。
USDT，USDC在coingecko只有部分链的合约地址信息；只能从其他地方补齐
************
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
************

假设ethereum链上的token已有一定积累，这时有一个新的A币，在ethereum链上，也可以执行下面的程序，把A币追加到文件ethereum里
python 030get_para_coin.PY  -f f:\\ethereum（结果保存） -chain ethereum（指定某链） -coin usd-coin wrapped-bitcoin（指定coingecko的id）

生成的ethereun是一个json文件，样式如下
{
    "BTC": {
        "URL_1":"https://api.paraswap.io/tokens/1",
        "id": "wrapped-bitcoin",
        "contract_address": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        "decimals": 8
    },
    "PEPE": {
        "id": "pepe",
        "contract_address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
        "decimals": 18
    }
}

（3）040produce_command.PY生成TargetCoinXXX文件，里面包含的是交易对的查价"指令"
python 040produce_command.PY -coin  ETH/USDT ETH/USDC "#"
-coin后面是指定的交易对
#表示此之前的是同一类token，可以检查是否有套利空间，当套利程序读取到#，则开始对之前的token进行套利检查。
ETH/USDT ETH/USDC "#"表示这一类都是ETH.
ETH/USDT ETH/USDC "#" BNB/USDT # 表示第一类是ETH资产，第二类是BNB资产。套利程序分别检查这两类资产是否有套利空间，注意，不是ETH和BNB混在一起套利，而是先查ETH是否能套利，再查BNB是否能套利。

040produce_command.PY 生成的是TargetCoinXXX文件一个用以获取价格的指令集合，包括DEX和CEX
格式为
PEPE/USDT,ethereum,openocean,DEX,SPOT,PEPE/USDT-ethereum-openocean,https://open-api.openocean.finance/v4/1/quote?inTokenAddress...
PEPE/USDT：交易对名字
ethereum：在什么链上
openocean：什么交易所
DEX：该交易所是DEX还是CEX
SPOT：该交易对是现货SPOT还是合约PERP
PEPE/USDT-ethereum-openocean：用于将后续的套利结果，输出到文件arbitrXXX，表示openocean交易所在eth链的PEPE/USDT交易对跟另外一个查询出来的，有套利空间。这样就可以直接到该交易所进行套利。
arbitr文件格式如下：
Arbitrage opportunities found:
openocean SPOT PEPE/USDT-openocean: 2.5e-05 vs paraswap SPOT PEPE/USDT-paraswap : 2.3e-05

对于PEPE等MEME币，单币价格太低，dex交易所paraswap显示不了准确单价（20241118价格为0.00002），只能用100或1000个MEME多少钱来折算出单价。因此这时的paraswap查询指令需要调整，即扩大查询倍数。通过以下指定将PEPE的查价指令扩展为查1000个PEPE，并且追加到TargetCoin_20241114143847文件中（之前已有的内容不覆盖）
python 040produce_command.PY -coin  PEPE/USDT "#" -N4paraswap 1000 -f TargetCoin_20241114143847
-N4paraswap 1000：是扩大到1000个token；此处可换为10或10000

考虑到普通币和单价很低的币，比较靠谱的方法是先输入一些价格大于1分的资产，例如ETH等；然后对于低价的币，例如PEPE，再补"PEPE+倍数"加到指定文件.这样就可以囊括你想要比价的资产，既有ETH也有PEPE。

（4）coin-1.PY默认对最新的TargetCoinxx文件里面的内容进行轮询，也可以选用指定文件。
该文件会生成arbitrxxx和pricesxxx文件，其中prices里面是查出来的价格；arbitr是套利的结果。

