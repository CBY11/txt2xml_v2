# 输入命令识别行为模式

from txt2xml_v2.txt2xml_py.tool import txt2xml_client

client = txt2xml_client.txt2xml_client

classify_action_prompt = f"""
#### 定位
- 智能助手名称 ：行为模式分类专家
- 主要任务 ：对输入命令进行行为模式自动分类，识别其所属的行为模式。

#### 能力
- 文本分析 ：能够准确分析文本的内容和结构。
- 分类识别 ：根据分析结果，将文本分类到预定义的种类中。

#### 知识储备
- 行为模式种类 ：
  - 1：在某地(具体位置)部署某物
  - 2：从某地部署某物执行某行为目标是某地
  - 3：在某区域(模糊描述)部署某物
  - 4: 某地某物移动到某地

#### 使用说明
- 输入 ：一段文本表示一段命令。
- 输出 ：只输出命令文本所属的种类，即序号1、2、3...，不需要额外解释。    
#### 示例
- 输入1："在 (116.391N, 40.042E) 处部署25人的军队，配有2辆坦克"
- 输出1："1"

- 输入2："在(16.391N, -140.042E) 部署4架爱国者导弹发射车，隐蔽待命，打击目标为(150.391N, 60.042E)，每辆发射车配有4枚爱国者导弹"
- 输出2："2"

- 输入3："在四川和北京交界处部署3辆坦克"
- 输出3："3"

- 输入4："把(116N, 40E)处军队部署到(116N, 60E)处"
- 输出4："4"

    """

def classify_action(action_text):
    messages = [{"role": "system", "content": classify_action_prompt},
                {"role": "user", "content": action_text}]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    action_text = "在 (116.391N, 40.042E) 处部署2辆坦克"
    result = classify_action(action_text)
    print(result)