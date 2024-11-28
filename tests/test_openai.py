from http.client import BAD_GATEWAY
import os
import xml.etree.ElementTree as ET
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from sympy import comp



def chat(user_content:str):

    system_content = """
    You are an intelligent classifier bot, Can classify user input in a quasi-grouped manner。
    Based on the user's input.All your responses need to refer to the following rules

    ## Rules
    response to user the following rules must be followed:

    + It is not allowed to output $$CategorizedList and $$IndustryList and $$assessmentList other than provided
    + Only one categorized, industry above can be used, choose the one that best matches
    + If it cannot be classified, the classification is -
    + replace the $category,$industry generated above
    + output must be in XML format as follows:

    ## Definition
    $$IndustryList = ['证券', '保险', '银行', '房地产', '白酒', '医药', '家电', '传媒', '通信', '半导体', '互联网', '军工', '新能源车', '光伏', '稀土', 'TMT', '信息技术', '电子', '黄金', '计算机', '农业', '食品饮料', '中药', '电力', '疫苗', '有色金属', '钢铁', '创新药', '煤炭', '建材', '化工', '交通运输', '环保', '基建', '汽车', '金融', '畜牧养殖', '动漫游戏', '机床', '石化', '医疗器械', '饮料', '汽油', '中证证保']
    $$CategorizedList = ['行业资讯', '大盘相关', '个股相关', '盘中走势', '其他']
    $$AssessmentList = ['利好','观望','利空']


    Use the following step-by-step instructions to respond to user inputs and reply only the result of step 7

    Step 0 - Initialize $1 and $2 to '-', Store the result as:
    ````
    <root>
        <category> $1 </category>
        <industry> $2 </industry>
        <assessment> $3 </assessment>
    </root>
    ````
    Step 1: Read the $$CategorizedList below
    Step 2: Read the user input, select the best one match from the $$CategorizedList as $1. If there is no match, set $category as '-'
    Step 3: If the result of $category is "行业资讯", execute step 4, otherwise return directly
    Step 4: Read the $$IndustryList below
    Step 5: Read the user input, select the best one match from $$IndustryList as $2
    Step 6: if (!$$IndustryList.includes($2)) set $2 to '-'
    Step 7: Read the $$assessmentList below
    Step 8: Read the user input, select the best one match from the $$AssessmentList as $3. If there is no match, set assessment as '-'
    Step 9: Result returned to user
    """

    completion = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
    )

    return completion

def get_content_to_json(completion):

    # 获取返回的 XML 内容
    content = completion.choices[0].message.content

    if content is None:
        raise ValueError("内容为空")
    match = re.search(r'```xml\n(.*?)\n```', content, re.DOTALL)

    if match:
        xml_content = match.group(1)
    else:
        raise ValueError("未找到有效的XML内容")

    # 解析 XML 内容
    root = ET.fromstring(xml_content)
    result = {child.tag: child.text for child in root}

    # 转换为 JSON 格式
    json_result = json.dumps(result, ensure_ascii=False, indent=4)
    return json_result

if __name__ == "__main__":
    _ = load_dotenv()

    XAI_API_KEY = os.getenv("XAI_API_KEY")
    BASE_URL = os.getenv("BASE_URL")

    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url=BASE_URL,
    )

    content = """
    转自：中工网工人日报-中工网记者 黄榆 通讯员 谢宏11月25日，昆明长水国际机场T2航站楼项目首块底板顺利完成浇筑，标志着航站楼取得重大进展，主体正式进入施工阶段。据中建三局西南公司副总经理、T2航站楼（北段）项目总包部总经理任志平介绍，自进场以来，项目团队牢固树立“今天再晚也是早、明天再早也是晚”的效率意识，始终坚持“价值创造，品质保障”企业核心价值观，周密安排施工部署，高效统筹各项资源，建设任务有序推进。本次浇筑两个工区同时展开，底板基础形式为桩承台基础，面积近6000平方米，混凝土方量超3000，连续浇筑时间近20小时。昆明长水国际机场T2航站楼项目是我国面向南亚、东南亚，连接欧亚的国际航空枢纽和前沿通道。项目建成后，将强化该机场国内和国际旅客的出发、到达及中转功能，推动云南省区域协调发展，为西南区域经济发展增添新动力。
    """
    comp = chat(content)
    print(get_content_to_json(comp))
