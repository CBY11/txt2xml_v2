import json
import os

import ollama
import chromadb

from . import txt2xml_client

# 加载实体
items = []
items_name = []
name_list = []
item_dir = os.environ.get("ITEM_DIR")
file_list = os.listdir(item_dir)
for file in file_list:
    with open(os.path.join(item_dir, file), "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        for item in data:
            name = item["name"]
            if "sub_model" not in item:
                items.append(item)
                name_list.append(name)
                for alias in item['alias_name']:
                    name_list.append(alias)
                    items_name.append([alias, name])
            else:
                tmp = item['sub_model']
                del item['sub_model']
                items.append(item)
                name_list.append(name)
                for alias in item['alias_name']:
                    name_list.append(alias)
                    items_name.append([alias, name])
                for model in tmp:
                    model_name = model["name"]
                    model['attribute'] = {**model["attribute"], **item['attribute']}
                    items.append(model)
                    name_list.append(model_name)
                    for model_alias in model['alias_name']:
                        name_list.append(model_alias)
                        items_name.append([model_alias, model_name])
print(name_list)
        # print(items_name)


prompt = f"""
#### 定位
- 智能助手名称 ：实体提取专家
- 主要任务 ：对输入的内容，提取其中出现的特定类型实体。

#### 能力
- 文本分析 ：准确理解文本内容。
- 分类识别 ：根据分析结果，提取文本中特定实体对象的名称。

#### 知识储备
- 需要提取的实体名称为涉及基地、飞机、舰船、导弹等特定领域的专有名词。地理位置等其他领域名词不需要提取。

#### 使用说明
- 输入 ：一段文本表示一段命令。
- 输出 ：以集合形式输出该段文本中所有符合条件的专有名词，要求不修改原文用词、不输出任何其他信息。若无符合要求名词则输出空集合。

#### 示例
- 输入1："在横须贺基地部署福特号航母"
- 输出1：["横须贺基地", "福特号航母"]

- 输入2："在伯克号驱逐舰上部署2枚战斧"
- 输出2：["伯克号驱逐舰", "战斧"]

- 输入3："嘉手纳基地的3架F35A飞往(0N, 180E)处"
- 输出3：["嘉手纳基地", "F35A"]

    """

# 加载向量数据库
embedding_model = "quentinz/bge-large-zh-v1.5"

chroma = chromadb.Client()
collection = chroma.create_collection(name="my_collection")
for i in range(0, len(name_list)):
    name = name_list[i]
    embed = ollama.embeddings(model=embedding_model, prompt=name)['embedding']
    collection.add(
        documents=[name],
        embeddings=[embed],
        ids=f"{i}"
    )

# model = SentenceTransformer('../bge-large-zh-v1.5')
# # 计算向量表示
# name_vectors = model.encode(name_list, show_progress_bar=False)
# # 构建 FAISS 索引
# index = faiss.IndexFlatL2(name_vectors.shape[1])
# index.add(np.array(name_vectors))

# limit = 0  查询阈值，暂不设置

def single_word_to_item(word):
    # Step 2: words to name of items (向量数据库)
    if word is None or word == '':
        return None
    # print(query)
    # query_vector = model.encode([word])
    # # 检索最相关文档
    # D, I = index.search(np.array(query_vector), k=1)
    # item_name, value = name_list[I[0][0]], D[0][0]
    # print(word, item_name, value)
    # if value > limit:
    #     real_name = item_name
    # else:
    #     print("低于阈值，舍去！")
    #     return None
    query_embed = ollama.embeddings(model=embedding_model, prompt=word)['embedding']
    results = collection.query(
        query_embeddings=[query_embed],
        n_results=3,  # 返回3个最相关知识块
        include=["documents", "distances"]
    )
    item_name, distance = results['documents'][0], results['distances'][0]
    print(word, item_name, distance)
    real_name = item_name[0]
    # Step 3: name of items to item
    for n in items_name:
        if n[0] == real_name:
            real_name = n[1]
            break
    for i in items:
        if i['name'] == real_name:
            return i
    return None


def text_to_item(text):
    # Step 1: text to words (大语言模型)
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": text}]
    words = eval(txt2xml_client.fast_gen_response(messages, False))
    print(words)
    # Step 2 & 3
    res = []
    for query in words:
        query_res = single_word_to_item(query)
        if query_res is not None:
            res.append(query_res)
    return res


# if __name__ == '__main__':
#     print(single_word_to_item("福建舰"))
