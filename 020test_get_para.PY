# -- coding:utf-8 --

import argparse
import os
import json


# 创建解析器
parser = argparse.ArgumentParser(description='检查并更新JSON文件')

# 添加第一个参数
parser.add_argument('param1', type=str, help='第一个参数')
# 添加第二个参数作为文件名
#parser.add_argument('filename', type=str, help='JSON文件名')
parser.add_argument('-f', '--filename', type=str, required=True, help='JSON文件名')
parser.add_argument('-coin', nargs='+', help='加密货币列表')
parser.add_argument('-chain', type=str, help='公链名字')

# 解析参数
args = parser.parse_args()

# 使用解析后的参数
print(f"第一个参数: {args.param1}")
print(f"文件名: {args.filename}")
#if args.coin:
print(f"chain:{args.chain}")
print(f"coin:{args.coin}")

# 检查文件是否存在
if os.path.exists(args.filename):
    # 文件存在，读取文件
    with open(args.filename, 'r') as file:
        data = json.load(file)
    print(f"文件 {args.filename} 已存在，内容已读取。")
else:
    with open(args.filename, 'w') as file:
        pass
