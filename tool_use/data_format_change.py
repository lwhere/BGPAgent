# 将case study相关的as path处理成跟bgp_leakage一致的格式
import json

def process_aspath_file(input_file, output_file):
    result = []
    with open(input_file, 'r') as infile:
        for line in infile:
            as_path = line.strip().split()
            formatted_as_path = "|".join(as_path)
            result.append({"as_path": formatted_as_path})
    
    with open(output_file, 'w') as outfile:
        json.dump(result, outfile, indent=4)

if __name__ == "__main__":
    input_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20121105_case_study_simple_path_moreVP_1.txt'  # 修改为实际输入文件路径
    output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20121105_case_study_aspath.json'  # 修改为实际输出文件路径
    process_aspath_file(input_file, output_file)
