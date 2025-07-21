# 对get_info中的name进行标准化，将其转换为标准化的形式，用于生成xml
import json

from txt2xml_v2.txt2xml_py.tool import txt2xml_client

client = txt2xml_client.txt2xml_client

standard_name_list = [
    "tank",
    "soldier",
    "missile-launcher",
    "missile"
]

name_standardizer_prompt = f"""
#### 定位
- 智能助手名称 ：名称归类专家
- 主要任务 ：对输入名称进行自动归类，识别其所属的标准名称。

#### 能力
- 分类识别 ：根据语义相似度，将输入名称分类到预定义的标准名称中。

#### 知识储备
- 标准名称 ：
  {standard_name_list}

#### 使用说明
- 输入 ：范围很宽泛的名称。
- 输出 ：只输出标准名称中和输入名称最相关的1个。    
#### 示例
- 输入1："坦克"
- 输出1："tank"

- 输入2："装甲车"
- 输出2："坦克"

- 输入3："爱国者导弹发射器"
- 输出3："missile-launcher"
"""

def get_standard_name(name):
    messages = [{"role": "system", "content": name_standardizer_prompt},
                {"role": "user", "content": name}]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0,
    )
    # print(response)
    return response.choices[0].message.content


def get_standard_json(json_obj, fields_to_standardize=None, standarder = get_standard_name):
    """
    递归遍历 json_obj，标准化指定字段（fields_to_standardize）中的值，
    使用 get_standard_name 函数对指定字段进行标准化。

    :param json_obj: 输入的 JSON 对象（可以是字典或列表）。
    :param fields_to_standardize: 要进行标准化的字段名称列表。
    :return: 返回一个新的 JSON 对象，其中指定的字段已被标准化。
    """
    if fields_to_standardize is None:
        fields_to_standardize = ["object_type", "object_name"]
    if isinstance(json_obj, dict):
        # 如果当前对象是字典类型，遍历其中的每一项
        for key, value in json_obj.items():
            # 如果值是嵌套的字典或列表，递归处理
            if isinstance(value, (dict, list)):
                json_obj[key] = get_standard_json(value, fields_to_standardize, standarder)
            # 如果当前键在 fields_to_standardize 中，并且值是字符串类型，则进行标准化
            elif key in fields_to_standardize:
                json_obj[key] = standarder(value)

    elif isinstance(json_obj, list):
        # 如果当前对象是列表类型，遍历其中的每个元素
        for idx, item in enumerate(json_obj):
            json_obj[idx] = get_standard_json(item, fields_to_standardize, standarder)

    return json_obj

def get_standard_xy(ne_num):
    return 1000 + float(ne_num) * 5



if __name__ == '__main__':
    # name = "武警"
    # standard_name = get_standard_name(name)
    # print(standard_name)
    json_obj = {
        "action_type": 2,
        "objects": [
            {
                "object_type": "爱国者导弹发射车",
                "number": 4,
                "longitude": 16.391,
                "latitude": -140.042,
                "action": "隐蔽待命",
                "target": {
                    "nickname": "null",
                    "longitude" : 150.391,
                    "latitude" : 60.042,
                },
                "object_asset":[
                    {
                        "object_type": "爱国者导弹",
                        "number": 4,
                    }
                ]
            },
        ]
    }

    standard_json_obj = get_standard_json(json_obj, fields_to_standardize=["object_type"], standarder=get_standard_name)
    standard_json_obj = get_standard_json(standard_json_obj, fields_to_standardize=["longitude", "latitude"], standarder=get_standard_xy)
    print(json.dumps(standard_json_obj, indent=4, ensure_ascii=False))