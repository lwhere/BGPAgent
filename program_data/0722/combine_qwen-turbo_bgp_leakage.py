import json
with open("/root/autodl-tmp/BGPAgent/program_data/0722/final_output/qwen-turbo_naive_p2c_final.json", "r") as f:
    naive_data = json.load(f)

with open("/root/autodl-tmp/BGPAgent/program_data/0722/final_output/qwen-turbo_asrank_series_p2c_final.json", "r") as f:
    asrank_data = json.load(f)

# 创建一个列表来存储所有合并后的数据
combined_data_list = []

# 假设两个列表长度相同，且对应索引的条目是相关的
for naive_entry, asrank_entry in zip(naive_data, asrank_data):

    combined_entry = naive_entry + asrank_entry[1:]
    # # 提取asrank推断结果的键和值
    # asrank_key = next(iter(naive_entry))
    # asrank_result = naive_entry[asrank_key]

    # # 提取问题和答案
    # question = asrank_entry["question"]
    # answer = asrank_entry["qwen-turbo-answer"]
    # answer_list = asrank_entry["qwen-turbo-answer-list"]

    # # 合并数据
    # combined_entry = {
    #     "as_path": asrank_key.split(" ")[9],  # 提取AS路径
    #     "asrank_inference_result": asrank_result,
    #     "question": question,
    #     "qwen-turbo-answer": answer,
    #     "qwen-turbo-answer-list": answer_list
    # }

    # 添加到列表中
    combined_data_list.append(combined_entry)

# 将合并后的数据保存到新的JSON文件中
with open("/root/autodl-tmp/BGPAgent/program_data/0722/qwen-turbo_combined_data.json", "w") as f:
    json.dump(combined_data_list, f, indent=4)

print("数据已合并，并保存到 'combined_data.json'")
