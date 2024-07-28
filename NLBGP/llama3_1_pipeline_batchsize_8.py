import json
import transformers
import torch
import re
import tqdm

from torch.utils.data import Dataset
from transformers import AutoTokenizer
class ListDataset(Dataset):
    items : list
    def __init__(self, items: list):
        self.items = items
    def __len__(self):
        return len(self.items)
    def __getitem__(self,idx):
        if torch.is_tensor(idx):
            idx = torch.tolist()
        return self.items[idx]

# 模型路径
model_id = "/root/autodl-tmp/Meta-Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# 系统提示
zero_shot_system_prompt_p2c = """
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS (Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c (provider-to-customer) and p2p (peer-to-peer).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like ["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

# 加载JSON数据
# with open("gpt4-turbo_20190606_case_study_as_group_20_pure+asrank_question_p2c.json", "r") as file:
#     data = json.load(file)

with open("llama3_20190606_case_study_as_group_3_pure+asrank_question_p2c.json", "r") as file:
    data = json.load(file)

# 加载模型
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)
pipeline.tokenizer.pad_token_id = tokenizer.eos_token_id
print(pipeline.tokenizer.pad_token_id)
# new
## preprocess
messages_list = []
messages_rag_list = []
for item in tqdm.tqdm(data):
    as_path = item[0].get("Please use the given as path and asrank algorithm to infer business relationships 268401|28598|12956|6830|21217|4134|174\n12726|32787|25091|21217|4134|174\n714|6830|21217|4134|174 asrank inference result", "")
    question = item[1].get("question", "")
    rag_question = item[2].get("question", "")
    
    messages = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": question},
    ]
    messages_list.append(messages)

    messages_rag = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": rag_question},
    ]
    messages_rag_list.append(messages_rag)

messages_dataset = ListDataset(messages_list)

for out in pipeline(messages_dataset, batch_size=8, temperature=0.01, max_new_tokens=8192):
    # test purpose
    print(out)
    break
import os
os.exit()

# before 
# 处理每个数据条目
results = []
for item in tqdm.tqdm(data):
    as_path = item[0].get("Please use the given as path and asrank algorithm to infer business relationships 268401|28598|12956|6830|21217|4134|174\n12726|32787|25091|21217|4134|174\n714|6830|21217|4134|174 asrank inference result", "")
    question = item[1].get("question", "")
    rag_question = item[2].get("question", "")
    
    messages = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": question},
    ]

    messages_rag = [
        {"role": "system", "content": zero_shot_system_prompt_p2c},
        {"role": "user", "content": rag_question},
    ]
    
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

    model_name = "Llama-3.1-8B-Instruct"
    
    # 提取生成的文本并保存结果
    value = output[0]["generated_text"][2]['content']
    rag_value = rag_output[0]["generated_text"][2]['content']
    pattern = re.compile(r'\[.*?\]', re.DOTALL)
    user_content = {}
    user_content['pure_question'] = question
    user_content[model_name+"-answer"] = value
    user_content[model_name+"-answer-list"] = pattern.findall(value)
    user_content['rag_question'] = rag_question
    user_content[model_name+"-rag-answer"] = rag_value
    user_content[model_name+"-rag-answer-list"] = pattern.findall(rag_value)
    print(user_content)
    # item.append(user_content)
    results.append(user_content)
    with open("cache.json", "w") as f:
        json.dump(results, f)
 
# 将结果保存到文件
output_filename = f"{datetime.today().strftime('%m%d')}_llama3.1_20190606_case_study_as_group_3_pure+asrank_question_p2c.json"
with open(output_filename, "w") as output_file:
    json.dump(results, output_file)

print(f"Results saved to {output_filename}")