import json

from . import txt2xml_client

simple_chat_prompt = ""
simple_chat_sys_prompt = ""
simple_chat_loop_prompt = ""


def start_chat(input_getter=input, ):
    print(simple_chat_prompt)
    history_messages = f"""system: {simple_chat_sys_prompt}\n"""
    while True:
        user_input = input_getter("请输入您的命令:")
        history_messages += f"""user: {user_input}\n"""
        messages = [{"role": "system", "content": simple_chat_loop_prompt},
                    {"role": "user", "content": history_messages}]
        response = txt2xml_client.fast_gen_response(messages, True)
        # print(response)
        response = json.loads(response)
        if response["command_is_clear"]:
            break
        else:
            history_messages += f"""system: {response["next_question"]}\n"""
            print(response["next_question"])
    return response["final_command"]


