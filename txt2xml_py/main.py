import os

import yaml

os.environ['AUDIO_DIR'] = r"F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\tmp\audio"
os.environ['ASR_DIR'] = r"F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\txt2xml_py\audio2txt"

from tool import action_classifier, get_info, name_standardizer, json2xml
from audio2txt import audio2txt_run




dest_xml_file = r'F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\xml_file\test_v2.html'
prompt_yaml = r"F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\config\prompt.yaml"


def init(yaml_file):
    # 加载 YAML 配置文件
    with open(yaml_file, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        action_classifier.classify_action_prompt = config["classify_action_prompt_front"] \
                                                   + config["classify_action_prompt_back"]

        get_info_templates = config.get("get_info_templates", [])
        get_info.get_info_template_list = []
        for i, template in enumerate(get_info_templates):
            get_info.get_info_template_list.append(template["get_info_template"])

        json2xml.find_op_action_list = config.get("find_op_action_list", [])


# 在 (120N, 40E) 处部署50人的军队，配有4辆坦克，5辆导弹发射车
# 在(15.812N, 50.7E) 部署4架爱国者导弹发射车，准备发射，打击目标为(-70.391N, 160.042E)，每辆发射车配有8枚爱国者导弹
# 在上海和北京交界处部署4架爱国者导弹发射车

if __name__ == '__main__':
    init(prompt_yaml)
    while True:
        # 部署somthing流程： input -> 识别行为类型 -> 依类型提取信息 -> 标准化名称、转换经纬度 -> 构建xml、修改xml文件
        # 修改somthing流程： input -> 识别行为类型 -> 依类型提取信息 -> 标准化名称、转换经纬度 ->  查找原xml中的标签  -> 构建xml、修改xml文件

        command = input("请输入命令: ")
        # command = get_txt_from_audio.get_txt_from_audio()
        # command = audio2txt_run.record_and_get_txt()  # 调用语音识别模块，返回命令字符串.
        print("命令: ", command)

        action_type = int(action_classifier.classify_action(command))
        print("行为类型识别结果: ", action_type)
        print(
            "========================================================================================================")

        info_json = get_info.get_info(command, action_type)
        print("信息提取结果: ", str(info_json))
        print(
            "========================================================================================================")

        std_info_json = name_standardizer.get_standard_json(info_json, fields_to_standardize=["object_type"],
                                                            standarder=name_standardizer.get_standard_name)
        std_info_json = name_standardizer.get_standard_json(std_info_json,
                                                            fields_to_standardize=["longitude", "latitude",
                                                                                   "old_longitude", "old_latitude"],
                                                            standarder=name_standardizer.get_standard_xy)
        print("信息标准化结果: ", str(std_info_json))
        print(
            "========================================================================================================")

        json2xml.modify_xml(std_info_json, dest_xml_file)
        print("命令已执行。")
        print(
            "========================================================================================================")
