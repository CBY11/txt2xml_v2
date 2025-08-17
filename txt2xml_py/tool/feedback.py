import random

# TODO
# 1. 与软件其他部分（主要是提示词）的调用关系
# 2. 持久化存储？
# 3. 取样策略

num_samples = 1     # few_shot提取正反样例的个数
list_positive, list_negative = [], []   # 每项样例为一个含"input""output"字段的字典

# 从样例列表中获取写入提示词的样例（目前采用随机策略）
def get_sample():
    # 样例列表对顺序不敏感，可以直接随机换序
    random.shuffle(list_positive)
    random.shuffle(list_negative)
    # 随机换序后取前n个
    return list_positive[:num_samples], list_negative[:num_samples]

# 储存用户反馈
def receive_feedback(input, output, response):
    if response:
        list_positive.append({"input": input, "output": output})
        print("用户正面反馈")
    else:
        list_negative.append({"input": input, "output": output})
        print("用户负面反馈")