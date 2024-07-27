import os

def process_file(file_path):
    output = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('|')
            if len(parts) < 10:
                continue
            as_path = parts[6].split()
            as_path_str = ' '.join(as_path)
            # print(as_path_str)
            # 这里需要修改next_as|leak_as|pre_as
            # if "3491 23947" in as_path_str:  #这个是2012.11.5的泄露三元组
            if "174 4134 21217" in as_path_str:  #这个是2019.6.6的泄露三元组
                reversed_as_path = ' '.join(as_path[::-1])
                output.append(reversed_as_path)
    return output

def main(directory):
    data_files = [f for f in os.listdir(directory) if f.endswith('.data')]
    for data_file in data_files:
        print(data_file)
        file_path = os.path.join(directory, data_file)
        output = process_file(file_path)
        # print(output)
        if output:
            output_file_path = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20190606_case_study.txt'
            with open(output_file_path, 'a+') as output_file:
                for line in output:
                    output_file.write(line + '\n')
            print(f'Processed {file_path} and output to {output_file_path}')

if __name__ == "__main__":
    directory = '/home/Phoenix/data/rrc00/2019.06'  
    main(directory)
