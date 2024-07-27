import os
import json
from tqdm import tqdm
from groq import Groq
from openai import OpenAI
import re
from BGPAgent.tool_use.prompt import *

openai_client = OpenAI(
    api_key=os.environ.get("AI_HUB_MIX_API_KEY"),
    base_url="https://aihubmix.com/v1"
)
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://groq.huggingtiger.asia/",
)


system_prompt = f"""{one_shot_system_prompt}"""

user_content_list = []
with open("./program_data/type1_input.json", "r") as f:
    user_content_list = json.load(f)

output_list = []

pattern = re.compile(r'\[.*?\]', re.DOTALL)


def get_client_chat_completion_value(client, model_name, args):
    print(args)
    chat_completion = client.chat.completions.create(
        model=model_name,
        **args
    )
    return chat_completion.choices[0].message.content


def update_user_content(user_content, model_name, value):
    user_content[model_name+"-answer"] = value
    user_content[model_name+"-answer-list"] = pattern.findall(value)
    return user_content


for user_content in tqdm(user_content_list):
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_content['question'],
        }]
    args = {
        "messages": messages,
        "temperature": 0.0,  # Optional
    }

    llama3_70b_value = get_client_chat_completion_value(
        groq_client, "llama3-70b-8192", args)
    user_content = update_user_content(
        user_content, "llama3-70b-8192", llama3_70b_value)

    llam3_8b_value = get_client_chat_completion_value(
        groq_client, "llama3-8b-8192", args)
    user_content = update_user_content(
        user_content, "llama3-8b-8192", llam3_8b_value)

    mistral_8_7b_value = get_client_chat_completion_value(
        groq_client, "mixtral-8x7b-32768", args)
    user_content = update_user_content(
        user_content, "mixtral-8x7b-32768", mistral_8_7b_value)

    gemma_7b_value = get_client_chat_completion_value(
        groq_client, "gemma-7b-it", args)
    user_content = update_user_content(
        user_content, "gemma-7b-it", gemma_7b_value)

    gpt_3__5_turbo_value = get_client_chat_completion_value(
        openai_client, "gpt-3.5-turbo", args)
    user_content = update_user_content(
        user_content, "gpt-3.5-turbo", gpt_3__5_turbo_value)

    gpt_4_turbo_value = get_client_chat_completion_value(
        openai_client, "gpt-4-turbo", args)
    user_content = update_user_content(
        user_content, "gpt-4-turbo", gpt_4_turbo_value)

    gpt_4o_value = get_client_chat_completion_value(
        openai_client, "gpt-4o", args)
    user_content = update_user_content(
        user_content, "gpt-4o", gpt_4o_value)

    claude_3__5_sonnet_value = get_client_chat_completion_value(
        openai_client, "claude-3-5-sonnet-20240620", args)
    user_content = update_user_content(
        user_content, "claude-3-5-sonnet-20240620", claude_3__5_sonnet_value)

    # print(user_content)
    output_list.append(user_content)
    with open("./program_data/cache/cache.json", "w", encoding='utf-8') as f:
        json.dump(output_list, f, ensure_ascii=False, indent=4)

output_path = "./program_data/0714/type1_english_output_0714_new_one_shot_prompt_temperation=0.json"

# 提取文件夹路径
folder_path = os.path.dirname(output_path)

# 检查文件夹是否存在，如果不存在则创建
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

with open(output_path, "w", encoding='utf-8') as f:
    json.dump(output_list, f, ensure_ascii=False, indent=4)
