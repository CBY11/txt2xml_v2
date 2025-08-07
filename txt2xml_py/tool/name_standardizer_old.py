# 对get_info中的name进行标准化，将其转换为标准化的形式，用于生成xml
import json

from . import txt2xml_client

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
    return txt2xml_client.fast_gen_response(messages, False)


def get_standard_obj(name, src_jsons):
    for obj in src_jsons:
        if name in obj["alias_name"]:
            return obj["name"], obj["attribute"]
    return name, {}


def get_standard_json(src_jsons, json_obj_to_std, fields_to_standardize=None, standarder=get_standard_obj):
    """
    递归遍历 json_obj，标准化指定字段（fields_to_standardize）中的值，
    使用 get_standard_name 函数对指定字段进行标准化。

    :param src_jsons: 知识库
    :param standarder: standardize 函数，用于对指定字段进行标准化。
    :param json_obj_to_std: 输入的 JSON 对象（可以是字典或列表）。
    :param fields_to_standardize: 要进行标准化的字段名称列表。
    :return: 返回一个新的 JSON 对象，其中指定的字段已被标准化。
    """
    if fields_to_standardize is None:
        fields_to_standardize = ["object_type", "object_name"]
    if isinstance(json_obj_to_std, dict):
        # 如果当前对象是字典类型，遍历其中的每一项
        for key, value in list(json_obj_to_std.items()):
            # 如果值是嵌套的字典或列表，递归处理
            if isinstance(value, (dict, list)):
                json_obj_to_std[key] = get_standard_json(src_jsons, value, fields_to_standardize, standarder)
            # 如果当前键在 fields_to_standardize 中，并且值是字符串类型，则进行标准化
            elif key in fields_to_standardize:
                json_obj_to_std[key], json_obj_to_std["attribute"] = standarder(value, src_jsons)

    elif isinstance(json_obj_to_std, list):
        # 如果当前对象是列表类型，遍历其中的每个元素
        for idx, item in enumerate(json_obj_to_std):
            json_obj_to_std[idx] = get_standard_json(src_jsons, item, fields_to_standardize, standarder)

    return json_obj_to_std


def get_standard_xy(ne_num):
    return 1000 + float(ne_num) * 5


if __name__ == '__main__':
    # name = "武警"
    # standard_name = get_standard_name(name)
    # print(standard_name)
    example_json = {
        "action_type": "1",
        "object": {
            "object_name": "福特号航空母舰",
            "longitude": "116.391",
            "latitude": "40.042",
            "object_asset": [
                {
                    "object_name": "闪电战斗机",
                    "number": "10"
                },
                {
                    "object_name": "民兵3",
                    "number": "20"
                }
            ]
        }
    }

    info_json = [
        {
            "name": "CVN78",
            "alias_name": [
                "杰拉尔德·R·福特号航空母舰",
                "福特号航空母舰"
            ],
            "type": "舰船",
            "type_name": "福特级航空母舰",
            "attribute": {
                "plane": True,
                "nuclear_power": True,
                "speed_knot": 30,
                "num_plane": 90
            }
        },
        {
            "name": "F-35",
            "alias_name": [
                "Lightning II",
                "闪电战斗机"
            ],
            "type": "战斗机",
            "attribute": {
                "speed_mach": 1.6,
                "stealth": True,
                "aircraft_gun": True,
                "max_height": 18300,
                "missile_load": []
            },
            "sub_model": [
                {
                    "name": "F-35A",
                    "alias_name": [],
                    "attribute": {
                        "on_ship": False,
                        "combat_radius": 1239
                    }
                },
                {
                    "name": "F-35B",
                    "alias_name": [],
                    "attribute": {
                        "on_ship": True,
                        "combat_radius": 935
                    }
                },
                {
                    "name": "F-35C",
                    "alias_name": [],
                    "attribute": {
                        "on_ship": True,
                        "combat_radius": 1240
                    }
                }
            ]
        },
        {
            "name": "LGM-30G",
            "alias_name": [
                "Minuteman III",
                "民兵3"
            ],
            "type": "导弹",
            "attribute": {
                "on_land": True,
                "on_ship": False,
                "on_plane": False,
                "to_land": True,
                "to_ship": False,
                "to_plane": False,
                "range": 13000,
                "num_warhead": 3
            }
        }
    ]

    std_info_json = get_standard_json(info_json, example_json,
                                      fields_to_standardize=["object_name"],
                                      standarder=get_standard_obj)
    print(json.dumps(std_info_json, indent=4, ensure_ascii=False))
