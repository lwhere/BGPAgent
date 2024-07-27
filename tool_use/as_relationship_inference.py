
import time
import os
import json
from tqdm import tqdm
import openai
import groq
import re
from prompt import *
import asyncio
from get_asrank_api_latest_result import get_as_information_from_as_path, get_as_information_from_as_paths, read_as_numbers_from_path
import call_asrank
from datetime import datetime



def extract_wait_time(error_message):
    import re
    # 修改正则表达式以匹配分钟和秒
    match = re.search(r"Please try again in (\d+)m(\d+\.?\d*)s", error_message)
    if match:
        # 提取分钟和秒
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        # 计算总秒数
        total_seconds = minutes * 60 + seconds + 60  # Add 60 seconds to be safe
        return total_seconds
    return 10 * 60  # Default wait time if not specified

def retry_request(max_retries=10, backoff_factor=0.3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (groq.APIConnectionError, openai.APIConnectionError) as e:
                    retries += 1
                    sleep_time = backoff_factor * (2 ** (retries - 1))
                    print(f"Retrying in {sleep_time} seconds due to connection error: {e}")
                    time.sleep(sleep_time)
                
                except groq.RateLimitError as e:
                    error_message = str(e)
                    retries += 1
                    wait_time = extract_wait_time(error_message)
                    print(f"Rate limit reached. Retrying in {wait_time} seconds.")
                    time.sleep(wait_time)
                    
                
                except groq.InternalServerError as e:
                    error_message = str(e)
                    if "Service Unavailable" in error_message:
                        print(f"Service unavailable. Retrying in 10 minitues due to internal server error: {e}")
                        time.sleep(10 * 60)
                    else:
                        print(f"Internal server error: {e}")
                        time.sleep(10 * 60)
                except openai.AuthenticationError as e:
                    error_message = str(e)
                    print(f"AiMixHub Service unavailable. Retrying in 600 seconds due to internal server error: {e}")
                    time.sleep(10 * 60)

                except openai.InternalServerError as e:
                    error_message = str(e)
                    if "Service Unavailable" in error_message:
                        print(f"Service unavailable. Retrying in {sleep_time} seconds due to internal server error: {e}")
                        time.sleep(10 * 60)
                    else:
                        print(f"Internal server error: {e}")
                        time.sleep(10 * 60)
                
                except e:
                    print(f"Unknown error: {e}")
                    print(f"Retrying in 10 minutes")
                    time.sleep(10 * 60)
                
    
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator



@retry_request(max_retries=5, backoff_factor=1)
def get_client_chat_completion_value(client, model_name, args):
    # print(args)
    chat_completion = client.chat.completions.create(
        model=model_name,
        **args
    )
    return chat_completion.choices[0].message.content


def update_user_content(user_content, model_name, value):
    pattern = re.compile(r'\[.*?\]', re.DOTALL)
    user_content[model_name+"-answer"] = value
    user_content[model_name+"-answer-list"] = pattern.findall(value)
    return user_content

# 预定义的API密钥列表
GROQ_API_KEYS = [
    os.environ.get("GROQ_API_KEY"),
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


def get_llm_user_content(question, model_series="llama3"):

    groq_client = groq.Groq(
    api_key=get_groq_api_key(),
    base_url="https://groq.huggingtiger.asia/",
)
    openai_client = openai.OpenAI(
    api_key=os.environ.get("AI_HUB_MIX_API_KEY"),
    base_url="https://aihubmix.com/v1"
)
    qwen_client = openai.OpenAI(
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
    deep_bricks_client = openai.OpenAI(
    api_key=os.environ.get("DEEP_BRICKS_API_KEY"),
    base_url="https://api.deepbricks.ai/v1/")

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
        "max_tokens": 2056
    }
    user_content = {"question": question}

    if model_series == "llama3":

        llama3_70b_value = get_client_chat_completion_value(
            groq_client, "llama3-70b-8192", args)
        user_content = update_user_content(
            user_content, "llama3-70b-8192", llama3_70b_value)
    
        llam3_8b_value = get_client_chat_completion_value(
            groq_client, "llama3-8b-8192", args)
        user_content = update_user_content(
            user_content, "llama3-8b-8192", llam3_8b_value)
        
    if model_series == "llama3.1":
        llama3_1_70b_value = get_client_chat_completion_value(
            groq_client, "llama-3.1-70b-versatile", args)
        user_content = update_user_content(
            user_content, "llama-3.1-70b-versatile", llama3_1_70b_value)
    
        llama3_1_8b_value = get_client_chat_completion_value(
            groq_client, "llama-3.1-8b-instant", args)
        user_content = update_user_content(
            user_content, "llama-3.1-8b-instant", llama3_1_8b_value)

    # mistral_8_7b_value = get_client_chat_completion_value(
    #     groq_client, "mixtral-8x7b-32768", args)
    # user_content = update_user_content(
    #     user_content, "mixtral-8x7b-32768", mistral_8_7b_value)

    # gemma_7b_value = get_client_chat_completion_value(
    #     groq_client, "gemma-7b-it", args)
    # user_content = update_user_content(
    #     user_content, "gemma-7b-it", gemma_7b_value)

    # gpt_3__5_turbo_value = get_client_chat_completion_value(
    #     openai_client, "gpt-3.5-turbo", args)
    # user_content = update_user_content(
    #     user_content, "gpt-3.5-turbo", gpt_3__5_turbo_value)

    if model_series == "gpt4-turbo":
        gpt_4_turbo_value = get_client_chat_completion_value(
            openai_client, "gpt-4-turbo", args)
        user_content = update_user_content(
            user_content, "gpt-4-turbo", gpt_4_turbo_value)
    
    elif model_series == "gpt4o":
        gpt_4o_value = get_client_chat_completion_value(
            openai_client, "gpt-4o", args)
        user_content = update_user_content(
            user_content, "gpt-4o", gpt_4o_value)
        
        gpt_4o_mini_value = get_client_chat_completion_value(
            openai_client, "gpt-4o-mini", args)
        user_content = update_user_content(
            user_content, "gpt-4o-mini", gpt_4o_mini_value)
        
    if model_series == "db-gpt-4-turbo":
        db_gpt_4_turbo_value = get_client_chat_completion_value(
            deep_bricks_client, "gpt-4-turbo", args)
        user_content = update_user_content(
            user_content, "gpt-4-turbo", db_gpt_4_turbo_value)
        
    if model_series == "claude-3-5":
        # claude_3_opus_value = get_client_chat_completion_value(
        #     openai_client, "claude-3-opus-20240229", args)
        # user_content = update_user_content(
        #     user_content, "claude-3-opus-20240229", claude_3_opus_value)
        
        # claude_3_sonnet_value = get_client_chat_completion_value(
        #     openai_client, "claude-3-sonnet-20240229", args)
        # user_content = update_user_content(
        #     user_content, "claude-3-sonnet-20240229", claude_3_sonnet_value)
        
        claude_3__5_sonnet_value = get_client_chat_completion_value(
            openai_client, "claude-3-5-sonnet-20240620", args)
        user_content = update_user_content(
            user_content, "claude-3-5-sonnet-20240620", claude_3__5_sonnet_value)
        
    if model_series == "qwen-max" or model_series == "qwen":
        qwen_max_value = get_client_chat_completion_value(
            qwen_client, "qwen-max", args)
        user_content = update_user_content(
            user_content, "qwen-max", qwen_max_value)

    if model_series == "qwen-turbo" or model_series == "qwen":    
        qwen_turbo_value = get_client_chat_completion_value(
            qwen_client, "qwen-turbo", args)
        user_content = update_user_content(
            user_content, "qwen-turbo", qwen_turbo_value)

    # else:
    #     raise Exception("Model series not supported")
    


    # print(user_content)
    output_list = []
    output_list.append(user_content)
    with open("/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0721/LLM_output_naive_s2s.json", "w", encoding='utf-8') as f:
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


# 读取input_list
def load_input_list(input_file_path):
    input_list = []
    with open(input_file_path, "r") as f:
        input_list = json.load(f)
    return input_list

def load_input_lines_to_list(input_file_path):
    with open(input_file_path, "r") as f:
        input_lines = f.readlines()
    input_list = []
    for line in input_lines:
        data = json.loads(line)
        input_list.append(data["as_path"].strip())
    return input_list


# 读取asrank api调用好的结果
def load_asrank_api_result(asrank_api_result_path="/home/yyc/BGP-Woodpecker/BGPAgent/program_data/asrank_api_result.json"):
    asrank_api_result = []
    if os.path.exists(asrank_api_result_path):
        with open(asrank_api_result_path, "r") as f:
            asrank_api_result = json.load(f)
    return asrank_api_result


# 增加中间结果的缓存机制
def load_cache_result(cache_path):
    # Create directory if it doesn't exist
    cache_dir = os.path.dirname(cache_path)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Load cache if exists
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding='utf-8') as f:
            inference_result_list = json.load(f)
    else:
        inference_result_list = []

    # Determine the starting point based on the current length of the inference result list
    start_index = len(inference_result_list)

    return inference_result_list, start_index



def main(input_file_path, cache_path, asrank_api_result_path, model_series):
    if "all-paths" in input_file_path:
        input_list = load_input_lines_to_list(input_file_path)
    else:
        input_list = load_input_list(input_file_path)
    inference_result_list, start_index = load_cache_result(cache_path)
    asrank_api_result = load_asrank_api_result(asrank_api_result_path)

    for idx, one_input in enumerate(tqdm(input_list)):
        if idx < start_index:
            continue

        if "gpt" in model_series and idx > 1000:
            break

        if "claude" in model_series and idx > 1000:
            break


        if type(one_input) == str:
            as_path = one_input
        
        elif len(one_input) == 1 or "as_path" in one_input:
            as_path = one_input["as_path"]
        else:
            as_path = '\n'.join(one_input.values())
        # 存储推理结果
        inference_result = []

        # # 调用asrank算法进行推断
        asrank_user_content = call_asrank.main(as_path).replace("# inferred clique: \n", "")
        if len(asrank_user_content) == 0:
            asrank_user_content = "asrank.pl inference algorithm can't infer the result due to the lack of information."
        as_rank_question = question_type_dict["call_asrank_question"]
        inference_result.append({f"{as_rank_question} {as_path} asrank inference result": asrank_user_content})

        # 从多个as_path获取到各个as的信息，as_paths是一个列表，每个列表的单个元素是一个字符串，
        # # 调用asrank api，从单个as_path获取到各个as的信息
        # ases_information_api = asyncio.run(get_as_information_from_as_path(aspath))

        # # 直接读取asrank api调用好的结果
        # ases_member = read_as_numbers_from_path(as_path)
        # ases_information = [item for item in asrank_api_result if item['retrived_asn'] in ases_member]
        
        ## 大模型推理问题
        ## 不提供其他附加信息直接推断
        pure_as_path_question = question_type_dict['pure_as_path_question']
        llm_user_content = get_llm_user_content(f"{pure_as_path_question}{as_path}.", model_series)
        inference_result.append(llm_user_content)


        # ## clique问题
        # llm_user_content = get_llm_user_content(f"{question_type_dict['add_clique_question']}.As path:{as_path}.Knowned clique member includes 174 209 286 701 1239 1299 2828 2914 3257 3320 3356 3491 5511 6453 6461 6762 6830 7018 12956.", model_series)
        # inference_result.append(llm_user_content)

        # ## transit传输度问题
        # asn_transit_map = get_asn_degree_map_for_json(ases_information)
        # llm_user_content = get_llm_user_content(f"{question_type_dict['add_transit_degree_question']}.As path: {as_path}.Transit degree information: {asn_transit_map}.", model_series)
        # inference_result.append(llm_user_content)

        # ## clique + transit degree问题
        # llm_user_content = get_llm_user_content(f"{question_type_dict['add_clique_transit_degree_question']}.As path: {as_path}.Known clique member includes 174 209 286 701 1239 1299 2828 2914 3257 3320 3356 3491 5511 6453 6461 6762 6830 7018 12956.Transit degree information: {asn_transit_map}.", model_series)
        # inference_result.append(llm_user_content)

        # # # 添加asrank.pl的推理结果
        # llm_user_content = get_llm_user_content(f"{question_type_dict['add_asrank_question']}.As path: {as_path}.Asrank algorithm inference result: {asrank_user_content}", model_series)
        # inference_result.append(llm_user_content)

        # combine asrank问题
        llm_user_content = get_llm_user_content(f"{question_type_dict['combine_asrank_question']}.As path: {as_path}.Asrank algorithm inference result: {asrank_user_content}", model_series)
        inference_result.append(llm_user_content)

        # 保存中间的cache结果
        inference_result_list.append(inference_result)
        with open(cache_path, "w", encoding='utf-8') as f:
            json.dump(inference_result_list, f, ensure_ascii=False, indent=4)
    
    output_path = cache_path.replace(".json", "_final.json").replace("cache", "final_output")
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(inference_result_list, f, ensure_ascii=False, indent=4)

question_type_dict = {}
question_type_path = "/home/yyc/BGP-Woodpecker/BGPAgent/program_data/question_type.json"
with open(question_type_path, "r") as f:
    question_type_dict = json.load(f)

# model_series = "gpt4-turbo"
# model_series = "db-gpt-4-turbo"
# model_series = "gpt4o"
# model_series = "claude-3-5"
# model_series = "llama3"
model_series = "llama3.1"
# model_series = "qwen-turbo"

experiment_name = f"{model_series}_all-paths_top5000_pure+asrank.pl_p2c"
system_prompt = f"""{zero_shot_system_prompt_p2c}"""

# input_file_path = "/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20190606_case_study_aspath.json"
input_file_path = "/home/yyc/BGP-Woodpecker/asrank_data/20240301_all-paths_cache_top_5000.json"
cache_path = f"/home/yyc/BGP-Woodpecker/BGPAgent/program_data/{datetime.today().strftime('%m%d')}/cache/{experiment_name}.json"
asrank_api_result_path = "/home/yyc/BGP-Woodpecker/asrank_data/20190606_case_study_aspath_asrank_api_result.json"


main(input_file_path, cache_path, asrank_api_result_path, model_series)





    









