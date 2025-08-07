# 根据指定的行为模式从命令文本中提取信息

import json

from . import txt2xml_client, action_classifier

get_info_template1 = """
    用户将提供一段文本，提取其中关于结构的信息，并以JSON格式输出。
    EXAMPLE INPUT : 
    在 (116.391N, 40.042E) 处部署25人的军队，配有2辆坦克
    EXAMPLE JSON OUTPUT :
    {
        "action_type": "1",
        "objects": [
            { 
                "object_type": "坦克",
                "number": "2",
                "longitude" : "116.391",
                "latitude" : "40.042",
            },
            { 
                "object_type": "军队",
                "number": "25",
                "longitude" : "116.391",
                "latitude" : "40.042",
            }
        ]
    }
"""

get_info_template2 = """
    用户将提供一段文本，提取其中关于结构的信息，并以JSON格式输出。
    EXAMPLE INPUT : 
    在(16.391N, -140.042E) 部署4架爱国者导弹发射车，隐蔽待命，打击目标为(150.391N, 60.042E)，每辆发射车配有4枚爱国者导弹

    EXAMPLE JSON OUTPUT :
    {
        "action_type": "2",
        "objects": [
            { 
                "object_type": "爱国者导弹发射车",
                "number": "4",
                "longitude": "16.391",
                "latitude": "-140.042",
                "action": "隐蔽待命"
                "target": {
                    "nickname": "null",
                    "longitude" : "150.391",
                    "latitude" : "60.042",
                }
                "object_asset":[
                    {
                        "object_type": "爱国者导弹",
                        "number": "4",
                    }
                ]
            },
        ]
    }
"""

get_info_template3 = """
    用户将提供一段文本，提取其中关于结构的信息，并以JSON格式输出。
    EXAMPLE INPUT : 
    在四川和北京交界处部署3辆坦克

    EXAMPLE JSON OUTPUT :
    {
        "action_type": "3",
        "objects": [
            { 
                "object_type": "坦克",
                "number": "3",
                "area": "四川和北京交界处"
            },
        ]
    }
"""

get_info_template4 = """
    用户将提供一段文本，提取其中关于结构的信息，并以JSON格式输出。
    EXAMPLE INPUT : 
    把(116N, 40E)处军队部署到(116N, 60E)处

    EXAMPLE JSON OUTPUT :
    {
        "action_type": "4",
        "objects": [
            { 
                "object_type": "军队",
                "old_longitude": "116",
                "old_latitude": "40",
                "longitude": "116",
                "latitude": "60"
            },
        ]
    }
"""

get_info_template_list = [
]

def get_info(text, action_type):
    messages = [{"role": "system", "content": get_info_template_list[action_type-1]},
                {"role": "user", "content": text}]
    return json.loads(txt2xml_client.fast_gen_response(messages, True))


if __name__ == '__main__':
    text = "在黄海沿岸处部署250人的军队，配有2架爱国者导弹发射器"
    action_type = action_classifier.classify_action(text)
    print(action_type)
    result = get_info(text, action_type)
    print(result)