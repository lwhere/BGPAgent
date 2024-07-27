import json
# 定义输入和输出文件路径
input_file = "alpaca_formatted_data.json"
output_file = "dummy_data.jsonl"

# 读取 alpaca 格式的数据
with open(input_file, 'r') as f:
    alpaca_data = json.load(f)

# 转换为 dummy_data 格式

count = 0
dummy_data = []
for item in alpaca_data:
    count += 1
    dummy_entry = {
        "conversation_id": count,
        "conversation": [
            {"human": item["instruction"] + " " + item["input"]},
            {"assistant": item["output"]}
        ]
    }
    dummy_data.append(dummy_entry)

# 保存为 JSONL 文件
with open(output_file, 'w') as f:
    for entry in dummy_data:
        json.dump(entry, f)
        f.write("\n")

print(f"Data successfully converted and saved to {output_file}")