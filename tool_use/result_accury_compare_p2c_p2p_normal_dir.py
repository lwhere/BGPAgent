import json
import sys
import os

# Function to normalize the relationship description
def normalize_relationship(rel):
    if rel == "-1":
        return "p2c"
    elif rel == "0":
        return "p2p"
    elif rel == "unknown":
        return "unknown"
    return None

# Function to parse AS relationships from File 2
def parse_as_relationships(file_path):
    as_relationships = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('|')
            if len(parts) == 3:
                as1, as2, rel = parts
                as_relationships[(as1, as2)] = normalize_relationship(rel)
                if rel == "0":
                    as_relationships[(as2, as1)] = normalize_relationship(rel)  # Assume symmetric relationships
    return as_relationships

# Function to extract and normalize relationships from the inference result
def extract_inferences_asrank(text):
    inferences = []
    
    lines = text.split('\n')
    for line in lines:
        if line:
            if "asrank.pl inference algorithm can't infer the result due to the lack of information." in line:
                continue
            if "No result from asrank.pl inference algorithm" in line:
                continue
            as_pair, rel = line.split('|')[:2], line.split('|')[2]
            as_pair_str = f"{as_pair[0]}-{as_pair[1]}"
            normalized_rel = normalize_relationship(rel)
            if normalized_rel:
                inferences.append(f"{as_pair_str}: {normalized_rel}")
    return inferences

def extract_inferences_llama(answers):
    business_relationships = []
    # 结果里有一个列表用这个
    # for answer in answers:
    #         if "Output" in answer:
    #             continue
    #         # Remove extra characters and split into individual relationships
    #         relationships = answer.strip('[]').replace('"', '')
    #         business_relationships.extend(relationships)
# 结果里多个列表用这个
    for answer in answers:
            if "Output" in answer:
                continue
            as_list=answer.strip('[]').split(',')
            for each_as in as_list:
                as_rel=each_as.strip('"').strip().strip('"')
                business_relationships.append(str(as_rel))
    return business_relationships
  

# Function to evaluate inferences
def evaluate_inferences_ASRank(inferences, as_relationships):
    correct = 0
    total = 0
    for inference in inferences:
        if inference.count('-') == 1 and inference.count(':')== 1:
            # 容错机制，有的as-rel中没有rel
            if inference[-2]!='2' or inference[-5]!=':':
                continue
            as_pair, inferred_rel = inference.split(': ')
            as1, as2 = as_pair.split('-')
            inferred_rel = inferred_rel.strip().lower()

            if inferred_rel == "unknown":
                continue  # Skip unknown inferences

            key = (as1, as2)
            if key in as_relationships:
                total += 1
                if as_relationships[key] == inferred_rel:
                    correct += 1

    accuracy = correct / total if total > 0 else 0
    return accuracy, correct, total

def evaluate_inferences_LLMs(inferences, as_relationships,ASRank_relationship):
    correct = 0
    total = 0
    p2p_p2p=0
    p2c_p2c=0
    for inference in inferences:
        if inference.count('-') == 1 and inference.count(':')== 1:
            # 容错机制，有的as-rel中没有rel
            if len(inference)<8:
                continue
            if inference[-2]!='2' or inference[-5]!=':':
                continue
            as_pair, inferred_rel = inference.split(': ')
            as1, as2 = as_pair.split('-')
            inferred_rel = inferred_rel.strip().lower()

            if inferred_rel == "unknown":
                continue  # Skip unknown inferences

            key = (as1, as2)
            if key in as_relationships:
                total += 1
                if as_relationships[key] == inferred_rel:
                    correct += 1
                
            if key in ASRank_relationship:
               if ASRank_relationship[key] == inferred_rel:
                    if inferred_rel == 'p2c':
                        p2c_p2c+=1
                    if inferred_rel == 'p2p':
                        p2p_p2p+=1

    accuracy = correct / total if total > 0 else 0
    return accuracy, correct, total, p2c_p2c, p2p_p2p

# 写一个asrank的结果转化
def parse_ASRank_relationship(ASRank_results):
    ASRank_relationship = {}
    for ASRank_result in ASRank_results:
        if ":" not in ASRank_result:
            continue
        if "-" not in ASRank_result:
            continue
        rel = ASRank_result.split(':')[1].strip(' ')
        as1 = ASRank_result.split('-')[0]
        as2 = ASRank_result.split('-')[1].split(':')[0]
        ASRank_relationship[(as1, as2)] = rel
        if rel == "p2p":
            ASRank_relationship[(as2, as1)] = rel
    return ASRank_relationship

def calculate_link_type(as_relationship):
    p2p=0
    p2c=0
    s2s=0
    for relation in as_relationship:
        if "unknown" in relation:
            continue
        if "..." in relation:
            continue
        if "-" not in relation:
            continue
        if ":" not in relation:
            continue
        val = relation.split(":")[1].strip(' ')
        if val =='p2p':
            p2p += 1
        elif val=="p2c" or val=="c2p":
            p2c += 1
        elif val=="s2s":
            s2s += 1
        
    return p2p,p2c,s2s


# Main function to process both sets of inferences
def main(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)
        # Extract asrank inference results
        asrank_inferences = []
        ASRank_relationship = []
        for entry in data1: 
            key_phrase = "asrank inference result"
            # Extract the content after the key phrase
            for key, value in entry[0].items():
                if key_phrase in key:
                    asrank_inferences.extend(extract_inferences_asrank(value))
        
        # 读取GT的结果
        as_relationships = parse_as_relationships(file2_path)
        # 将ASRank的结果也加入dict中
        ASRank_relationship = parse_ASRank_relationship(asrank_inferences)
        # Evaluate asrank inferences
        p2p_asrank,p2c_asrank,s2s_asrank=calculate_link_type(asrank_inferences)
        asrank_results = evaluate_inferences_ASRank(asrank_inferences, as_relationships)
        print(f"Question:\nASRank Inferences \nCorrect: {asrank_results[1]}, Total: {asrank_results[2]}, Accuracy: {asrank_results[0]:.2f}")
        print(f"There are {p2p_asrank} p2p links,{p2c_asrank} p2c links and {s2s_asrank} s2s links.")
        
        # Extract llama3-8b-8192 answers or chatgpt4-turbo
        if "llama3" in file1_path:
            model_key = 'llama3-8b-8192-answer-list'
        if "llama3.1" in file1_path:
            # model_key = 'llama-3.1-8b-instant-answer-list'
            model_key = 'llama-3.1-8b-instant-answer-list'
        if "gpt4" in file1_path:
            model_key = 'gpt-4-turbo-answer-list'
        if "gpt-4" in file1_path:
            model_key = 'gpt-4-turbo-answer-list'
        if "qwen" in file1_path:
            model_key = 'qwen-turbo-answer-list'
        if "claude-3" in file1_path:
            model_key = 'claude-3-5-sonnet-20240620-answer-list'
        llama3_answers = []
        print(len(data1[0]))
        for i in range(1,len(data1[0])):
            
            for entry in data1:
                # print(entry)
                # print(i)
                answer = entry[i].get(model_key, "")
                if answer:
                    llama3_answers.extend(extract_inferences_llama(answer))
            # print(f"Q{i+1}:")
            question_name = entry[i].get("question","").split('.')[0]
            print(f"Question:\n{question_name}")
            
            p2p_llama3,p2c_llama3,s2s_llama3=calculate_link_type(llama3_answers)
            
            # Evaluate llama3-8b-8192 inferences
            llama3_results = evaluate_inferences_LLMs(llama3_answers, as_relationships,ASRank_relationship)
            print(f"{model_key} Inferences \nCorrect: {llama3_results[1]}, Total: {llama3_results[2]}, Accuracy: {llama3_results[0]:.2f}")
            print(f"p2p: {p2p_llama3}({llama3_results[4]}/{p2p_asrank})   p2c: {p2c_llama3}({llama3_results[3]}/{p2c_asrank})")
            print(f"there are {p2p_llama3} p2p links,{p2c_llama3} p2c links and {s2s_llama3} s2s links.")
        print(f"")
    


# Example usage with file paths
# file1_path = '/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0723/final_output/llama3_20190606_case_study_all_question_p2c_final.json'
file2_path = '/home/yyc/BGP-Woodpecker/asrank_data/relationship_data/20240301.as-rel.txt'
sys.stdout = open('/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/log/result_accury_result_0801_1.log', 'w')   #控制输出到这个文件
file_dir ='/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0727/cache/'
files = os.listdir(file_dir)
files = [f for f in files if os.path.isfile(os.path.join(file_dir, f))]
for file in files:
    print(f"{file_dir}{file}")
    file1_path = file_dir+file
    main(file1_path, file2_path)
# main(file1_path, file2_path)

#现在不需要输出模型的名字了，可以根据路径实现自动匹配
# 每次运行只需要修改file1_path，结果会保存在result_accury_compare_p2c_p2p.log中


