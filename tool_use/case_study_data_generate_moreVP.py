def process_update_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if line.startswith("update|A|"):
                parts = line.strip().split('|')
                if len(parts) < 12:
                    continue
                as_path = parts[11]
                # 这里匹配泄露三元组
                if "3491 23947" in as_path:
                    reversed_as_path = ' '.join(as_path.split()[::-1])
                    # output_line = f"{parts[4]}|{reversed_as_path}\n"
                    output_line = f"{reversed_as_path}\n"
                    outfile.write(output_line)

if __name__ == "__main__":
    input_file = '/home/lwh/bgpstream-tutorial/download_20121105.log'  # 修改为实际输入文件路径
    output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20121105_case_study_moreVP_1.txt'  # 修改为实际输出文件路径
    process_update_file(input_file, output_file)
