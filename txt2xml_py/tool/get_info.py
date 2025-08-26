# 根据指定的行为模式从命令文本中提取信息

import json

from . import txt2xml_client, action_classifier

get_info_template1 = ""

get_info_template2 = ""

get_info_template3 = ""

get_info_template4 = ""

get_info_template_list = [
]


def get_info(text, action_type):
    messages = [{"role": "system", "content": get_info_template_list[action_type - 1]},
                {"role": "user", "content": text}]
    return json.loads((txt2xml_client.fast_gen_response(messages, True)).replace("\'", "\""))


if __name__ == '__main__':
    text = "在黄海沿岸处部署250人的军队，配有2架爱国者导弹发射器"
    action_type = action_classifier.classify_action(text)
    print(action_type)
    result = get_info(text, action_type)
    print(result)
