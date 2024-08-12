import json

# 输入和输出文件路径
input_file_path = '/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0726/final_output/llama3_all-paths_top5000_pure+asrank.pl_p2c_final.json'
output_file_path = 'llama3_all-paths_top1000_pure+asrank.pl_p2c_final_fine-tune-format.jsonl'

# 读取输入JSON文件
with open(input_file_path, 'r') as file:
    data = json.load(file)

# 准备输出数据的格式
output_lines = []

# 遍历每个对话
conversation_id = 1
for conversation in data:
    # if conversation_id > 2000:
    #     break
    # 初始化一个新的对话对象
    formatted_conversation = {
        "conversations_id": conversation_id,
        "conversations": []
    }

    # 遍历 conversation 内的每个消息
    for message in conversation:
        for key, value in message.items():
            if key == "question":
                # 如果存在已有的对话，先将其保存为一行
                if formatted_conversation["conversations"]:
                    output_lines.append(json.dumps(formatted_conversation, ensure_ascii=False))
                    # 更新 conversations_id
                    conversation_id += 1
                    # 开始一个新的对话
                    formatted_conversation = {
                        "conversations_id": conversation_id,
                        "conversations": []
                    }
                # 处理 human 的问题
                formatted_message = {
                    "from": "human",
                    "value": value
                }
                formatted_conversation["conversations"].append(formatted_message)
            elif "-answer" in key and "-answer-list" not in key and "8b" not in key:
                # 处理 gpt 的回答
                formatted_message = {
                    "from": "gpt",
                    "value": value
                }
                formatted_conversation["conversations"].append(formatted_message)

    # 处理最后一个对话
    if formatted_conversation["conversations"]:
        output_lines.append(json.dumps(formatted_conversation, ensure_ascii=False))
        conversation_id += 1

# 将输出数据行写入新的JSON文件，每行一个JSON对象
with open(output_file_path, 'w') as file:
    for line in output_lines:
        file.write(line + "\n")

print(f'转换后的数据已保存到 {output_file_path}')