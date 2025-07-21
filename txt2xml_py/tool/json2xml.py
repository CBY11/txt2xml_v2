# 从命令中提取出json格式的信息后转换为xml格式

from lxml import etree
import json
from bs4 import BeautifulSoup

from . import txt2xml_client

client = txt2xml_client.txt2xml_client
find_op_action_list = [4]

json2xml_background = """
    整个坐标屏幕大小为2000x2000，用户以中心x=1000，y=1000为中心，左上角为坐标原点,x轴向下为正方向，y轴向右为正方向，进行描述，
    longitude表示经度，latitude表示纬度，action表示动作，target表示目标，object_type表示对象类型，object_asset表示对象资产，
    longitude即x轴坐标，latitude即y轴坐标
    遵从上北下南左西右东的原则，例如东南即x>1000，y>1000，西北即x<1000，y<1000,东北即x>1000，y<1000，西南即x<1000，y>1000。
    tank的大小为200*200, soldier的大小为100*100, missile-launcher的大小为150*150,
    """

json2xml_prompt = """
用户将输入一个json对象，将其转换为xml格式:
背景信息如下：{ json2xml_background }

EXAMPLE JSON INPUT: 
{
    "action_type": 2,
    "objects": [
        {
            "object_type": "missile-launcher",
            "number": 4,
            "longitude": 1081.955,
            "latitude": 299.78999999999996,
            "action": "隐蔽待命",
            "target": {
                "nickname": "无",
                "longitude": 1751.955,
                "latitude": 1300.21
            },
            "object_asset": [
                {
                    "object_type": "missile",
                    "number": 4
                }
            ]
        }
    ]
}

EXAMPLE XML OUTPUT:
<g>
<rect fill="url(#missile-launcher_p)" height="150" width="150" x="1081" y="299">
    <title>
        详细信息：
        数量：4
        动作：隐蔽待命
        目标：
        目标位置：1751.955，1300.21
        武器配置：
        武器类型：missile
        数量：4
    </title>
</rect>
<use href="#aim" x="1751" y="1300"></use>
<line stroke="red" stroke-dasharray="5,5" stroke-width="2" x1="1081" x2="1751" y1="299" y2="1300"></line>
</g>
"""

json2xml_prompt = json2xml_prompt.replace("{ json2xml_background }", json2xml_background)


def json2xml(json_obj):
    messages = [{"role": "system", "content": json2xml_prompt},
                {"role": "user", "content": str(json_obj)}]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def find_op_ele(json_obj, xml_file_path):
    # 不会有重复的元素
    #

    # 查找对应元素
    # 加载 XML 文件
    tree = etree.parse(xml_file_path)

    # 获取 JSON 中的标签名称和属性
    tag_name = json_obj["tag_name"]
    attributes = json_obj["attributes"]

    # 遍历所有的 tag_name 标签
    matching_elements = []
    for elem in tree.xpath(f"//{tag_name}"):

        match = True
        for key, value in attributes.items():
            elem_value = elem.get(key)

            # 如果属性值是字典（表示范围），进行范围匹配（数字）
            if isinstance(value, float):
                # 检查属性是否可以转换为数字
                try:
                    num_value = float(elem_value)
                    if num_value < value['min'] or num_value > value['max']:
                        match = False
                        break
                except ValueError:
                    match = False
                    break

            # 如果是字符串，进行模糊匹配
            elif isinstance(value, str):
                if value not in elem_value:
                    match = False
                    break

        if match:
            matching_elements.append(elem)

    # 输出所有匹配的元素
    for elem in matching_elements:
        print(etree.tostring(elem))


def modify_xml(json_obj, xml_file_path):
    if json_obj['action_type'] not in find_op_action_list:
        xml_str = json2xml(json_obj)
        print("XML构建结果: ", xml_str)
        print(
            "========================================================================================================")
        new_ele = BeautifulSoup(xml_str, 'xml')  # 将文本字符串转为 BeautifulSoup 对象
    else:
        # 需要修改元素的情况
        pass

    # 读取 HTML 文件
    with open(xml_file_path, 'r', encoding='gbk') as file:
        html_content = file.read()

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # print(str(soup))

    # 创建新的 XML 标签（你可以插入任何XML文本格式的标签）

    # 查找 SVG 元素
    svg = soup.find('svg')  # 假设HTML中只有一个 <svg> 元素，或者你可以使用更具体的选择器

    # 获取<g>标签中所有的<rect>元素
    rects = new_ele.find_all('rect')
    # print(rects)

    try:
        # 记录初始x坐标
        current_x = float(rects[0]['x'])

        # 遍历所有<rect>标签并修改x坐标
        for rect in rects:
            # 获取当前矩形的宽度
            width = float(rect['width'])

            # 更新当前矩形的x坐标
            rect['x'] = str(current_x)

            # 为下一个矩形准备x坐标（当前矩形的x + 宽度）
            current_x += width
    except:
        pass

    rects = new_ele.find_all('rect')
    # print(rects)

    # 如果找到 SVG 元素，修改其中的内容
    if svg:
        svg.append(new_ele)  # 将新标签添加到 SVG 元素中

    # 将修改后的 HTML 保存到文件
    with open(xml_file_path, 'w', encoding='gbk') as file:
        file.write(str(soup))

    print("SVG 内容已修改并保存。")


if __name__ == '__main__':
    json_obj = {
        "action_type": 2,
        "objects": [
            {
                "object_type": "missile-launcher",
                "number": 6,
                "longitude": 581.955,
                "latitude": 350.78999999999996,
                "action": "瞄准目标",
                "target": {
                    "nickname": "null",
                    "longitude": 1751.955,
                    "latitude": 1300.21
                },
                "object_asset": [
                    {
                        "object_type": "missile-launcher",
                        "number": 4
                    }
                ]
            }
        ]

    }

    xml_str = """
    <g>
        <rect fill="url(#tank_p)" height="200" width="200" x="801" y="299">
            <title>
                详细信息：
                数量：4
            </title>
        </rect>
        <rect fill="url(#missile-launcher_p)" height="150" width="150" x="801" y="299">
            <title>
                详细信息：
                数量：5
            </title>
        </rect>
        <rect fill="url(#soldier_p)" height="100" width="100" x="801" y="299">
            <title>
                详细信息：
                数量：50
            </title>
        </rect>
    </g>
    """
    # xml_str = json2xml(json_obj)
    #
    xml_file_path = r'F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\xml_file\test_v2.html'
    modify_xml(xml_str, xml_file_path)
    # modify_xml(xml_str, xml_file_path)
