
# 将case study查找出来的路径去重
def process_aspath(input_file, output_path):
    seen_paths = set()
    with open(input_file, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            # 去除两端空白字符并按空格分割
            as_path = line.strip().split()
            # 去除重复的 AS
            unique_as_path = ' '.join(sorted(set(as_path), key=as_path.index))
            # 检查是否已经出现过
            if unique_as_path not in seen_paths:
                # 添加到 seen_paths 集合中
                seen_paths.add(unique_as_path)
                # 写入输出文件
                outfile.write(unique_as_path + '\n')

if __name__ == "__main__":
    input_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20121105_case_study_moreVP_1.txt'  # 修改为实际输入文件路径
    output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20121105_case_study_simple_path_moreVP_1.txt'  # 修改为实际输出文件路径
    process_aspath(input_file, output_file)
