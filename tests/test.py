import os
import re
from datetime import datetime

def parse_dates(content):
    content = content.split('----------------------------------------------------------------------------')[0]
    c_list = content.split('\n')
    c_list = c_list[1:][:-2]
    
    days = []
    for s in c_list:
        if s.startswith('买入日期'):
            buy_date = re.search(r'买入日期:(\d{8})', s).group(1)
            if datetime.strptime(buy_date, '%Y%m%d') < datetime(2019, 1, 1):
                continue
            days.append(('buy', buy_date))

        else:
            sell_date = re.search(r'卖出日期:(\d{8})', s).group(1)
            if not days:
                continue
            days.append(('sell', sell_date))
    
    if days and days[-1][0] == 'buy':
        current_date = datetime.now().strftime('%Y%m%d')
        days.append(('sell', current_date))

    total_days = 0
    for i in range(1, len(days), 2):
        buy_date = datetime.strptime(days[i-1][1], '%Y%m%d')
        sell_date = datetime.strptime(days[i][1], '%Y%m%d')
        total_days += (sell_date - buy_date).days


    return total_days


def main():
    directory = './data/yield'  # 替换为你的目录路径
    total_duration = 0
    for filename in os.listdir(directory):
        # print(f'正在处理文件: {filename[:6]}')  

        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                if '一次性买卖交易策略' in content:
                    total_days = parse_dates(content)

                    print(f'{filename[:6]}\t{total_days}\t天')