import json
import os
import yaml

with open("../config/prompt.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)
    enable_asr = config.get("enable_video", False)
    AUDIO_DIR = os.path.join(config["root_pth"], r"tmp\audio")
    ASR_DIR = os.path.join(config["root_pth"], r"txt2xml_py\audio2txt")
    src_xml_file = config["src_xml_file"]
    dest_xml_file = config["dest_xml_file"]
    prompt_yaml = config["prompt_yaml"]
    example_json = config.get("example_json", [])

os.environ['AUDIO_DIR'] = AUDIO_DIR
os.environ['ASR_DIR'] = ASR_DIR

from tool import action_classifier, get_info, json2xml
from tool import name_standardizer_old as name_standardizer

if enable_asr:
    from audio2txt import audio2txt_run

example_json_obj = []


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
        # print("加载配置文件成功。")
        # print(str(get_info.get_info_template_list))


        json2xml.json2xml_prompt = config["json2xml_prompt"]
        json2xml.json2xml_modify_prompt = config["json2xml_modify_prompt"]
        json2xml.find_op_action_list = config.get("find_op_action_list", [])

        example_json_files = config.get("example_json", [])
        for file in example_json_files:
            with open(file["json"], "r", encoding="utf-8") as f:
                example_json_obj.extend(json.load(f))


# 在120N，40E部署巴里号驱逐舰，配有5枚民兵3
# 在(15.812N, 50.7E) 部署朱沃特号驱逐舰，配有5枚战斧巡航导弹，打击目标为纽约
# 模糊描述
# 将福特号航空母舰调遣到 (116.391N, 40.042E) 处

if __name__ == '__main__':
    init(prompt_yaml)
    while True:
        # 部署somthing流程： input -> 识别行为类型 -> 依类型提取信息 -> 标准化名称、转换经纬度 -> 构建xml、修改xml文件
        # 修改somthing流程： input -> 识别行为类型 -> 依类型提取信息 -> 标准化名称、转换经纬度 ->  查找原xml中的标签  -> 构建xml、修改xml文件

        if enable_asr:
            # 调用语音识别模块，返回命令字符串.
            command = audio2txt_run.record_and_get_txt()  #  调用语音识别模块，返回命令字符串.
        else:
            command = input("请输入命令: ")

        print("命令: ", command)

        action_type = int(action_classifier.classify_action(command))
        print("行为类型识别结果: ", action_type)
        print(
            "========================================================================================================")

        info_json = get_info.get_info(command, action_type)
        print("信息提取结果: ", json.dumps(info_json, indent=4, ensure_ascii=False))
        print(
            "========================================================================================================")

        std_info_json = name_standardizer.get_standard_json(example_json_obj, info_json,
                                                            fields_to_standardize=["object_name"],
                                                            standarder=name_standardizer.get_standard_obj)
        # std_info_json = name_standardizer.get_standard_json(std_info_json,
        #                                                     fields_to_standardize=["longitude", "latitude",
        #                                                                            "old_longitude", "old_latitude"],
        #                                                     standarder=name_standardizer.get_standard_xy)
        print("信息标准化结果: ",json.dumps(std_info_json, indent=4, ensure_ascii=False))
        print(
            "========================================================================================================")

        json2xml.modify_xml(std_info_json, src_xml_file, dest_xml_file)
        print("命令已执行。")
        print(
            "========================================================================================================")
