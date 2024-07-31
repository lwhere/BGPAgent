import json
import transformers
import datetime
import torch
import re
import tqdm


# 模型路径
model_id = "/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-70B-Instruct"
model_id = "/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3.1-8B-Instruct"
model_id = "/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-405B-Instruct-FP8"

file_name = "zero_shot_llama3.1_all-paths_0-1000_pure+asrank_p2c_final_temperature=0.01_"

# 系统提示
zero_shot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like ["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

zero_shot_system_prompt_s2s = f"""
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS(Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c(provider-to-customer), p2p(peer-to-peer), s2s(sibling relationship).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

one_shot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

here is an example:
Input: Please use the given as path to infer business relationships:4608|7575|6461|8374|207694|207697|207694.
Output: Based on the given AS Path: 4608|7575|6461|8374|207694|207697|207694, I will infer the business relationships between each AS pair.\n\nTo infer the business relationships, I will use the following rules:\n\n* If an AS appears before another AS in the path, it is likely to be a provider (p) of the latter AS.\n* If an AS appears after another AS in the path, it is likely to be a customer (c) of the former AS.\n* If two ASes are adjacent in the path and have a similar transit degree (i.e., they are both transit networks or both stub networks), they are likely to be peers (p2p).\n\nHere are the inferred business relationships for each AS pair:\n\n* 4608-7575: p2c (4608 is a provider of 7575)\n* 7575-6461: p2c (7575 is a provider of 6461)\n* 6461-8374: p2c (6461 is a provider of 8374)\n* 8374-207694: p2c (8374 is a provider of 207694)\n* 207694-207697: p2p (207694 and 207697 are peers, as they are adjacent in the path and have a similar transit degree)\n* 207697-207694: p2p (207697 and 207694 are peers, as they are adjacent in the path and have a similar transit degree)\n\nNote that the last two AS pairs (207694-207697 and 207697-207694) have a peer-to-peer relationship, as they are adjacent in the path and have a similar transit degree.\n\nThe output list of business relationships is:\n\n[\"4608-7575: p2c\", \"7575-6461: p2c\", \"6461-8374: p2c\", \"8374-207694: p2c\", \"207694-207697: p2p\", \"207697-207694: p2p\"]

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like ["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""
# 加载JSON数据
# with open("gpt4-turbo_20190606_case_study_as_group_20_pure+asrank_question_p2c.json", "r") as file:
#     data = json.load(file)

with open("/root/autodl-tmp/BGPAgent/program_data/0726/cache/llama3_all-paths_top5000_pure+asrank.pl_p2c.json", "r") as file:
    data = json.load(file)


# with open("/root/autodl-tmp/BGPAgent/program_data/0722/qwen-turbo_combined_data_bgp_leakage.json", "r") as file:
#     data = json.load(file)


# 加载模型
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

# 处理每个数据条目
results = []
count = 0
for item in tqdm.tqdm(data):
    count += 1
    # if count < 2000:
    #     continue
    as_path = item[0].get("Please use the given as path and asrank algorithm to infer business relationships 268401|28598|12956|6830|21217|4134|174\n12726|32787|25091|21217|4134|174\n714|6830|21217|4134|174 asrank inference result", "")
    question = item[1].get("question", "")
    rag_question = item[2].get("question", "")
    # naive_rag_question = item[3].get("question", "")
    
    messages = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": question},
    ]

    messages_rag = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": rag_question},
    ]

    # naive_rag_message = [
    #     {"role": "system", "content": one_shot_system_prompt_p2c},
    #     {"role": "user", "content": naive_rag_question},
    # ]
    
    output = pipeline(
        messages,
        temperature=0.01,
        max_new_tokens=8192
    )

    rag_output = pipeline(
        messages_rag,
        temperature=0.01,
        max_new_tokens=8192
    )

    # naive_rag_output = pipeline(
    #     naive_rag_message,
    #     temperature=0.01,
    #     max_new_tokens=8192
    # )



    model_name = model_id.split("/")[-1]
    
    # 提取生成的文本并保存结果
    pattern = re.compile(r'\[.*?\]', re.DOTALL)
    user_content = {}

    value = output[0]["generated_text"][2]['content']
    user_content['pure_question'] = question
    user_content[model_name+"-answer"] = value
    user_content[model_name+"-answer-list"] = pattern.findall(value)

    rag_value = rag_output[0]["generated_text"][2]['content']
    user_content['rag_question'] = rag_question
    user_content[model_name+"-rag-answer"] = rag_value
    user_content[model_name+"-rag-answer-list"] = pattern.findall(rag_value)

    # naive_rag_message = naive_rag_output[0]["generated_text"][2]['content']
    # user_content['naive_rag_question'] = rag_question
    # user_content[model_name+"-naive-rag-answer"] = rag_value
    # user_content[model_name+"-naive-rag-answer-list"] = pattern.findall(rag_value)

    print(user_content)
    # item.append(user_content)
    results.append(user_content)
    with open(f"cache_{file_name}.json", "w") as f:
        json.dump(results, f)
 
# 将结果保存到文件
output_filename = f"0729_{file_name}_final.json"
with open(output_filename, "w") as output_file:
    json.dump(results, output_file)

print(f"Results saved to {output_filename}")