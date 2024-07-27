# 负责将case study 2019的数据转换为as path group

# def process_as_paths(input_file, output_file):
#     # 初始化AS集合和结果列表
#     as_set = set()
#     result_paths = []

#     # 读取输入文件
#     with open(input_file, 'r') as infile:
#         for line in infile:
#             as_path = line.strip().split()
#             as_path_set = set(as_path)
            
#             # 检查路径中的AS是否全部在已有集合中
#             if not as_path_set.issubset(as_set):
#                 # 将路径添加到结果列表中
#                 result_paths.append(line.strip())
#                 # 更新AS集合
#                 as_set.update(as_path_set)
    
#     # 写入输出文件
#     with open(output_file, 'w') as outfile:
#         for path in result_paths:
#             outfile.write(path + '\n')
#         outfile.write(str(len(as_set)))
            

# input_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20190606_case_study_simple_path.txt'  # 输入文件名
# output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/as_path_group_20190606_1.txt'  # 输出文件名


def process_as_paths(input_file, output_file):
    with open(input_file, 'r') as f:
        as_paths = f.readlines()

    as_set = set()
    as_path_set = set()
    output_list = []

    for path in as_paths:
        path = path.strip()
        as_list = path.split()
        path_tuple = tuple(as_list)
        
        # Check if all AS in the current path are in the as_set
        if all(asn in as_set for asn in as_list):
            continue

        # Remove subsets of the current AS path from as_path_set
        subsets_to_remove = {p for p in as_path_set if set(p).issubset(as_list)}
        as_path_set -= subsets_to_remove

        # Add the current AS path to the as_path_set and as_set
        as_path_set.add(path_tuple)
        as_set.update(as_list)
        
        # Add the current AS path to the output list
        output_list.append(path)
    
    # Write the final output list to the output file
    with open(output_file, 'w') as f:
        for path in output_list:
            f.write(path + '\n')

# Example usage:
input_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20190606_case_study_simple_path.txt'  # 输入文件名
output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/as_path_group_20190606.txt'  # 输出文件名
process_as_paths(input_file, output_file)



