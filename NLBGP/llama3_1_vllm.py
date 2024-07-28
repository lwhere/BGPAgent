import json
import transformers
from transformers import AutoTokenizer
import datetime
import torch
import re
import tqdm

# transformer part

# 模型路径

it_70b = "/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-70B-Instruct"
it_8b = "/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3.1-8B-Instruct"
model_id = it_8b
tokenizer = AutoTokenizer.from_pretrained(model_id)
file_name = f"one_shot_llama3.1_all-paths_5000+_pure+asrank_p2c_final_cuda=5_temperature=0.8_{model_id.split('/')[-1]}"

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


# 处理每个数据条目
messages_queue =[]
messages_rag_queue = []
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
        {"role": "system", "content": one_shot_system_prompt_p2c},
        {"role": "user", "content": question},
    ]

    messages_rag = [
        {"role": "system", "content": one_shot_system_prompt_p2c},
        {"role": "user", "content": rag_question},
    ]
    messages_queue.append(tokenizer.apply_chat_template(messages, tokenize=False))
    # naive_rag_message = [
    #     {"role": "system", "content": one_shot_system_prompt_p2c},
    #     {"role": "user", "content": naive_rag_question},
    # ]
    messages_rag_queue.append(tokenizer.apply_chat_template(messages_rag, tokenize=False))



    model_name = model_id.split("/")[-1]


# vllm part
from vllm import LLM
from vllm import LLM, SamplingParams
result_for_message = []
result_for_message_rag = []

sampling_params = SamplingParams(temperature=0.01, top_p=0.95, max_tokens=2048)
#/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3.1-8B-Instruct
#/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-70B-Instruct
llm = LLM(
    worker_use_ray=True,
    model=model_id,
    trust_remote_code=True,
    tensor_parallel_size=torch.cuda.device_count(),
    dtype="half",
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

outputs = llm.generate(messages_queue, sampling_params)
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    result_for_message.append(generated_text)
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")

import json
with open("./result_for_message.json", "a") as f:
    json.dump(result_for_message, f)

outputs = llm.generate(messages_rag_queue, sampling_params)
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    result_for_message_rag.append(generated_text)
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")

with open("./result_for_message_rag.json", "a") as f:
    json.dump(result_for_message_rag, f)

assert len(result_for_message) == len(result_for_message_rag)
failed_id = []
for i,(msg,rag) in enumerate(zip(result_for_message,result_for_message_rag)):
    try:
        # 提取生成的文本并保存结果
        pattern = re.compile(r'\[.*?\]', re.DOTALL)
        user_content = {}

        user_content['pure_question'] = question
        user_content[model_name+"-answer"] = msg
        user_content[model_name+"-answer-list"] = pattern.findall(msg)

        user_content['rag_question'] = rag_question
        user_content[model_name+"-rag-answer"] = rag
        user_content[model_name+"-rag-answer-list"] = pattern.findall(rag)

        # naive_rag_message = naive_rag_output[0]["generated_text"][2]['content']
        # user_content['naive_rag_question'] = rag_question
        # user_content[model_name+"-naive-rag-answer"] = rag_value
        # user_content[model_name+"-naive-rag-answer-list"] = pattern.findall(rag_value)

        print(user_content)
        # item.append(user_content)
        results.append(user_content)
        with open(f"cache_{file_name}.json", "w") as f:
            json.dump(results, f)
    except Exception as e:
        print(f"Failed on {i} for", e)
        failed_id.append(i)
 
# 将结果保存到文件
output_filename = f"0728_{file_name}_final.json"
with open(output_filename, "w") as output_file:
    json.dump(results, output_file)

print(f"Results saved to {output_filename}")

output_filename = f"0728_{file_name}_failed.json"
with open(output_filename, "w") as output_file:
    json.dump(failed_id, output_file)

print(f"Failed results saved to {output_filename}")

