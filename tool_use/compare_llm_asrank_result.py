import json
import re

# def parse_asrank_result(asrank_result):
#     # 解析asrank结果
#     lines = asrank_result.split("\n")
#     parsed_result = {}
#     for line in lines:
#         if line:
#             parts = line.split("|")
#             if len(parts) == 3:
#                 key = f"{parts[0]}-{parts[1]}"
#                 if parts[2] == "0":
#                     value = "p2p"
#                 else:
#                     value = "p2c" if parts[2] == "-1" else "c2p"
#                 parsed_result[key] = value
#     return parsed_result

# def parse_llama_result(llama_result_list):
#     # 解析llama结果
#     result_str = llama_result_list[-1]
#     pairs = re.findall(r'\"(\d+-\d+)\": (\w+)', result_str)
#     parsed_result = {pair[0]: pair[1] for pair in pairs}
#     return parsed_result

# def compare_results(asrank_result, llama_result):
#     # 比较两个结果
#     differences = {}
#     for key in asrank_result:
#         if key in llama_result:
#             if asrank_result[key] != llama_result[key]:
#                 differences[key] = (asrank_result[key], llama_result[key])
#         else:
#             differences[key] = (asrank_result[key], "missing in llama")
    
#     for key in llama_result:
#         if key not in asrank_result:
#             differences[key] = ("missing in asrank", llama_result[key])
    
#     return differences

with open("/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0720/cache/try_output_only_llama3_naive.json", "r") as f:
    data_list = json.load(f)


# for pair in data_list:
#     asrank_result = list(pair[0].values())[0].split("# inferred clique: \n")[-1]
#     llama_result_list = pair[1]["llama3-70b-8192-answer-list"]

#     parsed_asrank = parse_asrank_result(asrank_result)
#     parsed_llama = parse_llama_result(llama_result_list)

#     differences = compare_results(parsed_asrank, parsed_llama)

#     print("Differences:")
#     for key, value in differences.items():
#         print(f"{key}: asrank -> {value[0]}, llama -> {value[1]}")

def parse_asrank_result(asrank_result):
    # 解析asrank结果
    lines = asrank_result.split("\n")
    parsed_result = {}
    for line in lines:
        if line:
            parts = line.split("|")
            if len(parts) == 3:
                key = f"{parts[0]}-{parts[1]}"
                if parts[2] == "0":
                    value = "p2p"
                else:
                    value = "p2c" if parts[2] == "-1" else "c2p"
                parsed_result[key] = value
    return parsed_result

def parse_llama_result(llama_result_list):
    # 解析llama结果
    result_str = llama_result_list[-1]
    pairs = re.findall(r'\"(\d+-\d+)\": (\w+)', result_str)
    parsed_result = {pair[0]: pair[1] for pair in pairs}
    return parsed_result

def compare_results(asrank_result, llama_result):
    # 比较两个结果
    correct = 0
    total = len(asrank_result)
    differences = {}
    
    for key in asrank_result:
        if key in llama_result:
            if asrank_result[key] == llama_result[key]:
                correct += 1
            else:
                differences[key] = (asrank_result[key], llama_result[key])
        else:
            differences[key] = (asrank_result[key], "missing in llama")
    
    for key in llama_result:
        if key not in asrank_result:
            differences[key] = ("missing in asrank", llama_result[key])
    
    accuracy = correct / total if total > 0 else 0
    return differences, accuracy

# 读写进文件
f = open('/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/compare_result.txt', 'w')


for pair in data_list:
    asrank_result_str = list(pair[0].values())[0].split("# inferred clique: \n")[-1]
    llama_result_list = pair[1]["llama3-70b-8192-answer-list"]

    parsed_asrank = parse_asrank_result(asrank_result_str)
    parsed_llama = parse_llama_result(llama_result_list)

    differences, accuracy = compare_results(parsed_asrank, parsed_llama)

    f.writelines("Differences:\n")
    for key, value in differences.items():
        f.writelines(f"{key}: asrank -> {value[0]}, llama -> {value[1]}\n")
    
    f.writelines(f"Accuracy: {accuracy * 100:.2f}%\n")