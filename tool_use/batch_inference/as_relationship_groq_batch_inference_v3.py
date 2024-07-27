import time
import os
import json
from tqdm.asyncio import tqdm as tqdm_asyncio
import openai
import groq
import re
from prompt import *
import asyncio

from get_asrank_api_latest_result import get_as_information_from_as_path, get_as_information_from_as_paths, read_as_numbers_from_path

import call_asrank

system_prompt = f"""{one_shot_system_prompt}"""

output_list = []

def extract_wait_time(error_message):
    import re
    match = re.search(r"Please try again in (\d+\.?\d*)s", error_message)
    if match:
        return float(match.group(1))
    return 0  # Default wait time if not specified

def retry_request(max_retries=3, backoff_factor=0.3):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except (groq.APIConnectionError, openai.APIConnectionError) as e:
                    retries += 1
                    sleep_time = backoff_factor * (2 ** (retries - 1))
                    print(f"Retrying in {sleep_time} seconds due to connection error: {e}")
                    await asyncio.sleep(sleep_time)
                except groq.RateLimitError as e:
                    error_message = str(e)
                    if "rate_limit_reached" in error_message:
                        wait_time = extract_wait_time(error_message)
                        print(f"Rate limit reached. Retrying in {wait_time} seconds.")
                        await asyncio.sleep(wait_time)
                    else:
                        raise e
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator

@retry_request(max_retries=5, backoff_factor=1)
async def get_client_chat_completion_value(client, model_name, args):
    chat_completion = await asyncio.to_thread(client.chat.completions.create, model=model_name, **args)
    return chat_completion.choices[0].message.content

def update_user_content(user_content, model_name, value):
    pattern = re.compile(r'\[.*?\]', re.DOTALL)
    user_content[model_name+"-answer"] = value
    user_content[model_name+"-answer-list"] = pattern.findall(value)
    return user_content

# 预定义的API密钥列表
GROQ_API_KEYS = [
    "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",
    "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",
    "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"
]

# 轮训计数器
counter = 0

def get_groq_api_key():
    global counter
    api_key = GROQ_API_KEYS[counter % len(GROQ_API_KEYS)]
    counter += 1
    return api_key

async def get_llm_user_content(question):
    groq_client = groq.Groq(
        api_key=get_groq_api_key(),
        base_url="https://groq.huggingtiger.asia/",
    )
    openai_client = openai.OpenAI(
        api_key=os.environ.get("AI_HUB_MIX_API_KEY"),
        base_url="https://aihubmix.com/v1"
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": question
        }]
    args = {
        "messages": messages,
        "temperature": 0.0,  # Optional
    }
    user_content = {"question": question}

    llama3_70b_value = await get_client_chat_completion_value(
        groq_client, "llama3-70b-8192", args)
    user_content = update_user_content(
        user_content, "llama3-70b-8192", llama3_70b_value)

    output_list.append(user_content)
    with open("/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0720/LLM_output_naive.json", "w", encoding='utf-8') as f:
        json.dump(output_list, f, ensure_ascii=False, indent=4)

    return user_content

def get_asn_degree_map_for_json(ases_information):
    result_list = []
    for data in ases_information:
        retrived_asn = data.get('retrived_asn')
        as_info = data.get('as_information')
        if as_info:
            asn_degree = as_info.get('asnDegree')
            if asn_degree:
                transit = asn_degree.get('transit')
                if transit is not None:
                    result_list.append(f"{retrived_asn}: {transit}")
                else:
                    result_list.append(f"{retrived_asn}: transit information not available")
            else:
                result_list.append(f"{retrived_asn}: ASN degree information not available")
        else:
            result_list.append(f"{retrived_asn}: AS information not available")

    asn_transit_map = ', '.join(result_list)
    return asn_transit_map

# 读取处理好的报文数据，调用call_asrank api，并将结果存储下来
raw_data_input_path = "/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/bgp_leakage.json"
input_list = []
with open(raw_data_input_path, "r") as f:
    input_list = json.load(f)

# 增加中间结果的缓存机制
cache_path = "/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0720/cache/try_output_only_llama3.json"
# Load cache if exists
if os.path.exists(cache_path):
    with open(cache_path, "r", encoding='utf-8') as f:
        inference_result_list = json.load(f)
else:
    inference_result_list = []

# Determine the starting point based on the current length of the inference result list
start_index = len(inference_result_list)

# 读取asrank api调用好的结果
with open("/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/bgpleak_filtered_as_information_latest_result.json", "r") as f:
    all_ases_information = json.load(f)

question_type_dict = {}
with open("/home/yyc/BGP-Woodpecker/BGPAgent/program_data/question_type.json", "r") as f:
    question_type_dict = json.load(f)

async def process_as_paths(as_paths):
    pure_as_path_question = question_type_dict["pure_as_path_question"]
    tasks = [get_llm_user_content(f"{pure_as_path_question}. as path 为 {aspath}.") for aspath in as_paths]
    return await tqdm_asyncio.gather(*tasks)

async def main():

    for idx in tqdm_asyncio(range(start_index, len(input_list), len(GROQ_API_KEYS)), desc="Processing Batches"):
        as_paths = [one_input["as_path"] for one_input in input_list[idx:idx + len(GROQ_API_KEYS)]]
        inference_results = await process_as_paths(as_paths)

        for i, one_input in enumerate(input_list[idx:idx + len(GROQ_API_KEYS)]):
            aspath = one_input["as_path"]
            inference_result = []
            # # 调用asrank算法进行推断
            # asrank_user_content = call_asrank.main(aspath)
            # as_rank_question = question_type_dict["call_asrank_question"]
            # inference_result.append(
            #     {f"{user_content_list[0]} {aspath} asrank inference result": asrank_user_content})

            # 从多个as_path获取到各个as的信息，as_paths是一个列表，每个列表的单个元素是一个字符串，
            # # 调用asrank api，从单个as_path获取到各个as的信息
            # ases_information_api = asyncio.run(get_as_information_from_as_path(aspath))

            # 直接读取asrank api调用好的结果
            ases_member = read_as_numbers_from_path(aspath)
            ases_information = [item for item in all_ases_information if item['retrived_asn'] in ases_member]

            # 大模型推理问题
            # 不提供其他附加信息直接推断
            llm_user_content = inference_results[i]
            inference_result.append(llm_user_content)

            # # clique问题
            # llm_user_content = get_llm_user_content(f"{user_content_list[2]}. as path 为 {aspath}.目前已知的clique为174 209 286 701 1239 1299 2828 2914 3257 3320 3356 3491 5511 6453 6461 6762 6830 7018和12956。")
            # inference_result.append(llm_user_content)

            # # transit传输度问题
            # asn_transit_map = get_asn_degree_map_for_json(ases_information)
            # llm_user_content = get_llm_user_content(f"{user_content_list[3]}. as path 为 {aspath}, transit degree 为 {asn_transit_map}.")
            # inference_result.append(llm_user_content)

            inference_result_list.append(inference_result)

            with open(cache_path, "w", encoding='utf-8') as f:
                json.dump(inference_result_list, f, ensure_ascii=False, indent=4)

    output_path = "/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0720/try_output_only_llama3.json"
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(inference_result_list, f, ensure_ascii=False, indent=4)

asyncio.run(main())
