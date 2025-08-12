from openai import OpenAI
import ollama

llm_name = "webapi_dpv3"

txt2xml_client_webapi_dpv3 = OpenAI(
    api_key="sk-645c13592ea34fc38c776779a0c01b77",
    base_url="https://api.deepseek.com",
)


def gen_response_webapi_dpv3(messages, json_format):
    if json_format:
        response = txt2xml_client_webapi_dpv3.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0,
            response_format={
                'type': 'json_object'
            },
        )
    else:
        response = txt2xml_client_webapi_dpv3.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0,
        )
    return response.choices[0].message.content


def gen_response_ollama_dp32b(messages, response_format):
    if response_format:
        response = ollama.chat(
            model='deepseek-r1:32b',
            messages=messages,
            think=False,
            format='json',
            options={'temperature': 0}
        )
        return response['message']['content']
    else:
        response = ollama.chat(
            model='deepseek-r1:32b',
            messages=messages,
            think=False,
            options={'temperature': 0},
        )
        return response['message']['content']

def fast_gen_response(messages, json_format):
    if llm_name == "webapi_dpv3":
        return gen_response_webapi_dpv3(messages, json_format)
    elif llm_name == "ollama_dp32b":
        return gen_response_ollama_dp32b(messages, json_format)
    return "fail"

