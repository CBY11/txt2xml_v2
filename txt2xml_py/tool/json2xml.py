# 从命令中提取出json格式的信息后转换为xml格式

from lxml import etree
import json
from bs4 import BeautifulSoup

from . import txt2xml_client

find_op_action_list = [4]

json2xml_prompt = """
用户将输入一个json对象，将其转换为xml格式:
EXAMPLE JSON INPUT: 
  {
    "action_type": "1",
    "object": {
      "object_name": "CVN78",
      "longitude": "116.391",
      "latitude": "40.042",
      "attribute": {
        "plane": "True",
        "nuclear_power": true,
        "speed_knot": 30,
      },
      "object_assets": [
        {
          "object_name": "LGM-30G",
          "number": "20",
          "attribute": {
            "on_land": true,
            "to_plane": false,
            "range": 13000,
          }
        }
      ],
      "object_targets": [
        {
          "name": "New York",
          "attribute": {
            "lat": 40.7128,
            "lon": -74.0060,
            "people_count": 8804190
          }
        }
      ]
    }
  }

EXAMPLE XML OUTPUT:
<Factory name="CVN78">
        <FactoryWaypoints> 
            <WaypointTableEntry> 
                <Lat>116.391</Lat> 
                <Lon>40.042</Lon>
                <Alt>0</Alt> 
                <latest/>
            </WaypointTableEntry>
        </FactoryWaypoints>
        <FactoryAttributes>
            <plane>true</plane>
            <nuclear_power>true</nuclear_power>
            <speed_knot>30</speed_knot>
        </FactoryAttributes>
        <SomethingLoad>
            <Name>LGM-30G</Name> 
            <Count>20</Count>
            <SomethingLoadAttributes> 
                <UseSystemDefaultSomething>True</UseSystemDefaultSomething>
                <on_land>true</on_land>
                <to_plane>false</to_plane>
                <range>13000</range>
            </SomethingLoadAttributes>
        </SomethingLoad>
        <Target>
            <TargetTable> 
                <TargetTableEntry> 
                    <Name>New York</Name>
                    <Latitude>40.7128</Latitude>
                    <Longitude>-74.0060</Longitude>
                    <Population>8804190</Population>
                </TargetTableEntry>
            </TargetTable>
        </Target>
    </Factory>
"""

json2xml_modify_prompt = """
    用户将输入一个json对象和一个字符串形式的xml标签，将json对象中可能包含的信息更新到xml中有关的元素上标签，格式化输出xml字符串
    EXAMPLE INPUT: 
        json:
        {
            "action_type": "1",
            "object": {
              "object_name": "CVN78",
              "longitude": "116.391",
              "latitude": "40.042",
              "object_asset": [
              ],
              "attribute": {
              }
            }
          } 
        xml:
        <Factory name="CVN78">
            <FactoryWaypoints> <!-- 航母、舰艇 途径点 -->
                <WaypointTableEntry> <!-- 途径点 -->
                    <Lat>44.0</Lat> <!-- 北纬 -->
                    <Lon>-10.0</Lon> <!-- 东经 -->
                    <Alt>0</Alt> <!-- 海拔 -->
                </WaypointTableEntry>
                <WaypointTableEntry> <!-- 途径点 -->
                    <Lat>45.0</Lat> <!-- 北纬 -->
                    <Lon>-10.0</Lon> <!-- 东经 -->
                    <Alt>0</Alt> <!-- 海拔 -->
                    <latest/><!-- 最新目标点 -->
                </WaypointTableEntry>
            </FactoryWaypoints>
        </Factory> 
        
    EXAMPLE OUTPUT:
        <Factory name="CVN78">
            <FactoryWaypoints> <!-- 航母、舰艇 途径点 -->
                <WaypointTableEntry> <!-- 途径点 -->
                    <Lat>44.0</Lat> <!-- 北纬 -->
                    <Lon>-10.0</Lon> <!-- 东经 -->
                    <Alt>0</Alt> <!-- 海拔 -->
                </WaypointTableEntry>
                <WaypointTableEntry> <!-- 途径点 -->
                    <Lat>45.0</Lat> <!-- 北纬 -->
                    <Lon>-10.0</Lon> <!-- 东经 -->
                    <Alt>0</Alt> <!-- 海拔 -->
                </WaypointTableEntry>
                <WaypointTableEntry> <!-- 途径点 -->
                    <Lat>116.391</Lat> <!-- 北纬 -->
                    <Lon>40.042</Lon> <!-- 东经 -->
                    <Alt>0</Alt> <!-- 海拔 -->
                    <latest/><!-- 最新目标点 -->
                </WaypointTableEntry>
            </FactoryWaypoints>
        </Factory> 
"""


def extract_xml_from_string(input_string):
    # 找到被 ```xml``` 包裹的部分
    start_tag = '```xml'
    end_tag = '```'

    # 查找开始和结束的位置
    start_index = input_string.find(start_tag)
    end_index = input_string.find(end_tag, start_index + len(start_tag))

    if start_index != -1 and end_index != -1:
        # 提取 xml 内容
        return input_string[start_index + len(start_tag):end_index].strip()
    else:
        return input_string  # 如果没找到 XML 部分


def json2xml(json_obj):
    messages = [{"role": "system", "content": json2xml_prompt},
                {"role": "user", "content": str(json_obj)}]
    return txt2xml_client.fast_gen_response(messages, False)


def json2xml_modify(json_obj, old_xml_str):
    messages = [{"role": "system", "content": json2xml_modify_prompt},
                {"role": "user", "content":
                    f"""json:
                    {str(json_obj)}
                    xml:
                    {old_xml_str}
                    """}]
    return txt2xml_client.fast_gen_response(messages, False)


def modify_xml(json_obj, src_xml_file_path, xml_file_path):
    # 读取 XML 文件
    with open(src_xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # 使用 BeautifulSoup 解析 XML
    soup = BeautifulSoup(xml_content, 'xml')

    # 查找 <Factory> 标签，匹配其 name 属性
    factory = soup.find('Factory', {'name': json_obj["object"]["object_name"]})

    if factory:
        # 找到匹配的 <Factory> 标签，执行后续操作
        # print(f"Found matching <Factory> with name: {json_obj['name']}")
        # 在这里执行你需要的修改逻辑
        xml_str = json2xml_modify(json_obj, str(factory))  # 使用 json2xml_modify 转换为 XML 字符串
        xml_str = extract_xml_from_string(xml_str)
        new_ele = BeautifulSoup(xml_str, 'xml')
        factory.replace_with(new_ele)  # 替换原有元素
    else:
        # 没有找到匹配的 <Factory> 标签，执行其他操作
        # print(f"No matching <Factory> found with name: {json_obj['name']}")
        # 这里可以添加需要的操作，可能是创建新的元素或其他逻辑
        xml_str = json2xml(json_obj)  # 使用 json2xml 转换为 XML 字符串
        xml_str = extract_xml_from_string(xml_str)
        new_ele = BeautifulSoup(xml_str, 'xml')
        g = soup.find('g')  # 假设最外层是 <g> 标签
        g.append(new_ele)

    print("XML构建结果: ", xml_str)
    print(
        "========================================================================================================")

    # 将修改后的 HTML 保存到文件
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    print("XML 内容已修改并保存。")
    return xml_str


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
