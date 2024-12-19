import os
import re
from datetime import datetime

def parse_dates(title, content):
    c_list = content.split('\n')
    start_find_end = False
    for i, s in enumerate(c_list):
        if title in s:
            c_list = c_list[i+1:]
            start_find_end = True
        elif start_find_end and '----------------------------------------------------------------------------' in s:
            c_list = c_list[:i-2]
            break
    if "指数估值数据不满5年" in c_list:
        return 0
    # print(c_list)

    days = []
    temp_sell = None
    for s in c_list:
        if s.startswith('买入日期'):
            if temp_sell:
                dd = temp_sell
                days.append(('sell', dd))
                temp_sell = None
            buy_date = re.search(r'买入日期:(\d{8})', s).group(1)
            if datetime.strptime(buy_date, '%Y%m%d') < datetime(2019, 1, 1):
                continue
            days.append(('buy', buy_date))
        else:
            sell_date = re.search(r'卖出日期:(\d{8})', s).group(1)
            if not days:
                continue
            temp_sell = sell_date
    if temp_sell:
        dd = temp_sell
        days.append(('sell', dd))
    
    if days and days[-1][0] == 'buy':
        current_date = datetime.now().strftime('%Y%m%d')
        days.append(('sell', current_date))

    # print(days)

    total_days = 0
    for i in range(1, len(days), 2):
        buy_date = datetime.strptime(days[i-1][1], '%Y%m%d')
        sell_date = datetime.strptime(days[i][1], '%Y%m%d')
        total_days += (sell_date - buy_date).days


    return total_days


def main():
    directory = './data/yield'  # 替换为你的目录路径
    title = '估值买卖交易策略' # 替换为你的标题
    # is_test = True
    is_test = False

    for filename in os.listdir(directory):
        # print(f'正在处理文件: {filename[:6]}')  
        if filename.endswith('.txt'):
            if is_test and not filename.startswith('000001'):
                continue
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                if title in content:
                    total_days = parse_dates(title, content)
                    print(f'{filename[:6]}\t{total_days}\t天')