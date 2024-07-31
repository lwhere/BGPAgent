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
model_id = it_70b
tokenizer = AutoTokenizer.from_pretrained(model_id)
file_name = f"zero_shot_vllm_all-paths_0-1000_pure+asrank_no_system_prompt_final_cuda=0-3_temperature=0.01_{model_id.split('/')[-1]}"

# 系统提示

zero_shot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

Output: ASN1-ASN2: <Business Relationship>, you must return the results as a list which looks like ["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

zero_shot_cot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like ["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

zero_shot_cot_system_prompt_s2s = f"""
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

Input: Please use the given as path to infer business relationships:15562|2914|58453|9808|56047.
Output:To determine the business relationships between AS nodes in the given AS path \"15562|2914|58453|9808|56047\", we analyze the path from left to right, considering the typical flow of traffic from a provider to a customer or between peers.\n\n1. **15562 to 2914**: AS2914 (NTT America, Inc.) is a major global provider known for its extensive peering and customer base. AS15562 is likely smaller in comparison. The relationship is likely provider-to-customer (p2c), with AS2914 being the provider to AS15562.\n\n2. **2914 to 58453**: AS58453 (China Mobile International) is a large network, but given AS2914's global reach and status, the relationship here would also typically be provider-to-customer (p2c), with AS2914 serving as the provider to AS58453.\n\n3. **58453 to 9808**: AS9808 (Guangdong Mobile Communication Co.Ltd.) is a large mobile network in China. Given that AS58453 is part of China Mobile International, this relationship is likely provider-to-customer (p2c), with AS58453 being the provider to AS9808.\n\n4. **9808 to 56047**: AS56047 (China Mobile communications corporation) is also part of the larger China Mobile group. The relationship between AS9808 and AS56047, both being part of the same corporate group, is typically provider-to-customer (p2c), with AS9808 acting as the provider to AS56047.\n\nBased on this analysis, the business relationships in the AS path are:\n- **15562-2914: p2c**\n- **2914-58453: p2c**\n- **58453-9808: p2c**\n- **9808-56047: p2c**\n\nOutput:\n[\"15562-2914: p2c\", \"2914-58453: p2c\", \"58453-9808: p2c\", \"9808-56047: p2c\"]
"""

two_shot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

here are two examples:

Input: Please use the given as path to infer business relationships:15562|2914|58453|9808|56047.
Output:To determine the business relationships between AS nodes in the given AS path \"15562|2914|58453|9808|56047\", we analyze the path from left to right, considering the typical flow of traffic from a provider to a customer or between peers.\n\n1. **15562 to 2914**: AS2914 (NTT America, Inc.) is a major global provider known for its extensive peering and customer base. AS15562 is likely smaller in comparison. The relationship is likely provider-to-customer (p2c), with AS2914 being the provider to AS15562.\n\n2. **2914 to 58453**: AS58453 (China Mobile International) is a large network, but given AS2914's global reach and status, the relationship here would also typically be provider-to-customer (p2c), with AS2914 serving as the provider to AS58453.\n\n3. **58453 to 9808**: AS9808 (Guangdong Mobile Communication Co.Ltd.) is a large mobile network in China. Given that AS58453 is part of China Mobile International, this relationship is likely provider-to-customer (p2c), with AS58453 being the provider to AS9808.\n\n4. **9808 to 56047**: AS56047 (China Mobile communications corporation) is also part of the larger China Mobile group. The relationship between AS9808 and AS56047, both being part of the same corporate group, is typically provider-to-customer (p2c), with AS9808 acting as the provider to AS56047.\n\nBased on this analysis, the business relationships in the AS path are:\n- **15562-2914: p2c**\n- **2914-58453: p2c**\n- **58453-9808: p2c**\n- **9808-56047: p2c**\n\nOutput:\n[\"15562-2914: p2c\", \"2914-58453: p2c\", \"58453-9808: p2c\", \"9808-56047: p2c\"]

Input: Please consider the AS path results and the ASrank algorithm results comprehensively, and combine your own judgment to infer AS business relationships..As path: 4608|7575|6461|8374|207694|207697|207694.Asrank algorithm inference result: asrank.pl inference algorithm can't infer the result due to the lack of information.
Output: A challenging one!\n\nGiven the AS path and the lack of information from the ASrank algorithm, I'll have to rely on my own judgment and general knowledge of BGP business relationships. Here's my analysis:\n\nAS Path: 4608|7575|6461|8374|207694|207697|207694\n\n1. 4608-7575: p2c (provider-to-customer)\nReasoning: 4608 is a large Chinese ISP (China Telecom), and 7575 is a smaller Australian ISP (Macquarie Telecom). It's likely that 7575 is a customer of 4608, as 4608 has a larger global presence and more extensive network infrastructure.\n\n2. 7575-6461: p2p (peer-to-peer)\nReasoning: 7575 (Macquarie Telecom) and 6461 (Abovenet Communications) are both mid-sized ISPs with significant international presence. Given their similar size and scope, it's likely they have a peering agreement, exchanging traffic on a settlement-free basis.\n\n3. 6461-8374: p2c (provider-to-customer)\nReasoning: 6461 (Abovenet Communications) is a larger ISP with a more extensive network, while 8374 (PlusNet) is a smaller UK-based ISP. It's likely that 8374 is a customer of 6461, as 6461 has a larger network and more resources.\n\n4. 8374-207694: p2c (provider-to-customer)\nReasoning: 8374 (PlusNet) is a smaller ISP, and 207694 (a European ISP) is likely a customer of 8374, given the smaller size and regional focus of 207694.\n\n5. 207694-207697: p2p (peer-to-peer)\nReasoning: Both 207694 and 207697 are European ISPs with similar sizes and regional focus. It's likely they have a peering agreement, exchanging traffic on a settlement-free basis.\n\n6. 207697-207694: p2p (peer-to-peer)\nReasoning: Same reasoning as above; both ASNs are likely peers, given their similar characteristics.\n\nPlease note that these inferences are based on general knowledge and may not reflect the actual business relationships between these ASNs. The output list of business relationships is:\n\n[\"4608-7575: p2c\", \"7575-6461: p2p\", \"6461-8374: p2c\", \"8374-207694: p2c\", \"207694-207697: p2p\", \"207697-207694: p2p\"]
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
    if count >= 1000:
        break
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

