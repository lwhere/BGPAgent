import json

def read_as_paths(input_file):
    with open(input_file, 'r') as f:
        return [line.strip().split() for line in f.readlines()]


# 如果需要对每组多少条路径修改，只需要改以下的两个数字和最后的输出目录
def format_as_json(as_paths):
    formatted_paths = []
    for i in range(0, len(as_paths), 20):
        group = as_paths[i:i+20]
        entry = {}
        for j, path in enumerate(group):
            entry[f"number{j+1}"] = '|'.join(path)
        formatted_paths.append(entry)
    return formatted_paths

def write_to_json(output_file, formatted_paths):
    with open(output_file, 'w') as f:
        json.dump(formatted_paths, f, indent=4)

def main(input_file, output_file):
    as_paths = read_as_paths(input_file)
    formatted_paths = format_as_json(as_paths)
    write_to_json(output_file, formatted_paths)


# Example usage:
input_file = 'as_path_group_20190606.txt'
output_file = 'as_path_group_20190606_20paths.json'
main(input_file, output_file)
