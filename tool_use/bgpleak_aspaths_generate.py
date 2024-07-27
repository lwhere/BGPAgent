# 主要用于将bgpleak的泄露数据在caida上的aspaths搜索并扩充数据集


# import json

# def load_data(aspaths_file, bgpleak_file):
#     with open(aspaths_file, 'r') as f:
#         aspaths = [json.loads(line) for line in f]
#     with open(bgpleak_file, 'r') as f:
#         bgpleak = json.load(f)
#     return aspaths, bgpleak

# def find_matching_aspaths(aspaths, bgpleak_entry):
#     # match_key = f"{bgpleak_entry['next_node']}-{bgpleak_entry['leak_node']}-{bgpleak_entry['pre_node']}"
#     # 修改匹配为leak AS-pre AS
#     match_key = f"{bgpleak_entry['leak_node']}-{bgpleak_entry['pre_node']}"
#     matching_aspaths = []
    
#     for entry in aspaths:
#         if match_key in entry['as_path']:
#             matching_aspaths.append(entry['as_path'])
#         if len(matching_aspaths) >= 10:
#             break
#     return matching_aspaths

# def save_results(bgpleak, results, output_file):
#     output_data = []
#     for entry, matches in zip(bgpleak, results):
#         output_data.append({
#             "bgpleak_as_path": entry['as_path'],
#             "matching_aspaths": matches[::-1]  # Reverse the list of matching ASPATHs
#         })
    
#     with open(output_file, 'w') as f:
#         json.dump(output_data, f, indent=4)

# def main(aspaths_file, bgpleak_file, output_file):
#     aspaths, bgpleak = load_data(aspaths_file, bgpleak_file)
    
#     results = []
#     for entry in bgpleak:
#         matches = find_matching_aspaths(aspaths, entry)
#         results.append(matches)
    
#     save_results(bgpleak, results, output_file)


import json

def load_bgpleak(bgpleak_file):
    with open(bgpleak_file, 'r') as f:
        bgpleak = json.load(f)
    return bgpleak

def find_matching_aspaths(aspaths_file, bgpleak_entry):
    match_key = f"{bgpleak_entry['next_node']}|{bgpleak_entry['leak_node']}|{bgpleak_entry['pre_node']}"
    # match_key = f"{bgpleak_entry['leak_node']}|{bgpleak_entry['pre_node']}"
    matching_aspaths = []
    
    with open(aspaths_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            as_path = parts[1]
            if match_key in as_path:
                matching_aspaths.append(as_path)
            if len(matching_aspaths) >= 10:
                break
    return matching_aspaths

def save_results(bgpleak, results, output_file):
    output_data = []
    for entry, matches in zip(bgpleak, results):
        output_data.append({
            "bgpleak_as_path": entry['as_path'],
            "matching_aspaths": matches[::-1]  # Reverse the list of matching ASPATHs
        })
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

def main(aspaths_file, bgpleak_file, output_file):
    bgpleak = load_bgpleak(bgpleak_file)
    
    results = []
    for entry in bgpleak:
        matches = find_matching_aspaths(aspaths_file, entry)
        results.append(matches)
    
    save_results(bgpleak, results, output_file)

# if __name__ == "__main__":
#     aspaths_file = 'aspaths.txt'  # Assuming the aspaths data is stored in a text file
#     bgpleak_file = 'bgpleak.json'
#     output_file = 'output.json'
    
#     main(aspaths_file, bgpleak_file, output_file)


if __name__ == "__main__":
    aspaths_file = '/home/yyc/BGP-Woodpecker/asrank_data/20240301.all-paths'
    bgpleak_file = '/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/bgp_leakage.json'
    output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/generated_bgpleak_allpaths.json'

    # 输出文件为allpaths时，为三元组完整匹配
    # 输出文件为two_as_match，为pre_AS和leak_AS的匹配
    
    main(aspaths_file, bgpleak_file, output_file)
