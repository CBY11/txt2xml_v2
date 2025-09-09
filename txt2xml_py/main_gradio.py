import gradio as gr
import xml.etree.ElementTree as ET
import json

# 模拟的XML和JSON数据
xml_data = '''<root>
    <element>
        <name>Example</name>
        <value>1</value>
    </element>
    <element>
        <name>Sample</name>
        <value>2</value>
    </element>
</root>'''

json_data = [
    {"key": "value1"},
    {"key": "value2"},
    {"key": "value3"}
]


# 将XML数据和JSON数据格式化为字符串
def format_data():
    # 解析XML
    xml_tree = ET.ElementTree(ET.fromstring(xml_data))
    xml_str = ET.tostring(xml_tree.getroot(), encoding='unicode', method='xml')

    # 格式化JSON数据
    json_str = json.dumps(json_data, indent=4)

    return xml_str, json_str


# 模型对话功能
def chatbot(input_text):
    # 这里可以替换成你的模型对话逻辑
    return f"你说的是: {input_text}"


# 获取格式化数据
xml_str, json_str = format_data()

# 创建Gradio界面
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Row():  # 用于左右分块
                # 左侧原始 JSON 数据
                with gr.Accordion("原始 JSON 数据", open=False):
                    json_output_original = gr.Textbox(
                        label="",
                        interactive=True,
                        value=json.dumps(json_data, indent=4),
                        scale=1,
                        elem_id="json_output_original"  # 给元素一个ID以用于CSS样式
                    )

                # 右侧标准化后的 JSON 数据
                with gr.Accordion("标准化后的 JSON 数据", open=False):
                    json_output_standardized = gr.Textbox(
                        interactive=True,
                        value=json.dumps(json_data, indent=4),  # 确保有 standardized_json_data
                        scale=1,
                        elem_id="json_output_original"  # 给元素一个ID以用于CSS样式
                    )
            gr.Textbox(label="XML 数据", interactive=False, lines=20, value=xml_str)

        with gr.Column(scale=1):
            input_text = gr.Textbox(label="输入你的问题", placeholder="在这里输入...")
            output_text = gr.Textbox(label="模型回复", interactive=False)
            submit_btn = gr.Button("提交")

            submit_btn.click(chatbot, inputs=input_text, outputs=output_text)


# CSS 样式
demo.css = """
#json_output_original, #json_output_standardized {
    border: none;  /* 取消边框 */
    overflow-y: auto;  /* 内容过长时纵向滚动 */
    resize: none; /* 禁用用户调整大小 */
    height: 200px; /* 可自定义高度 */
}
"""

# 启动Gradio应用
demo.launch()
