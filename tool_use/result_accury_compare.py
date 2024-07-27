import json

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
    for answer in answers:
            if "Output" in answer:
                continue
            # Remove extra characters and split into individual relationships
            relationships = answer.strip('[]').replace('"', '').split(', ')
            business_relationships.extend(relationships)
    return business_relationships
  

# Function to evaluate inferences
def evaluate_inferences(inferences, as_relationships):
    correct = 0
    total = 0
    for inference in inferences:
        if inference.count('-') == 1 and inference.count(':')== 1:
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

def calculate_link_type(as_relationship):
    p2p=0
    p2c=0
    s2s=0
    for relation in as_relationship:
        if "unknown" in relation:
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
        for entry in data1: 
            key_phrase = "asrank inference result"
            # Extract the content after the key phrase
            for key, value in entry[0].items():
                if key_phrase in key:
                    # print(value)  
            # result = entry[0].get("请根据所给路径使用asrank推断as商业关系。 47394|6939|6762|42313|12713|3320|174|52320|7738|8167|28646 asrank inference result", "")
                    asrank_inferences.extend(extract_inferences_asrank(value))
        
        # Extract llama3-8b-8192 answers
        llama3_answers = []
        for entry in data1:
            answer = entry[1].get("llama3-8b-8192-answer-list", "")
            if answer:
                llama3_answers.extend(extract_inferences_llama(answer))

    p2p_asrank,p2c_asrank,s2s_asrank=calculate_link_type(asrank_inferences)
    p2p_llama3,p2c_llama3,s2s_llama3=calculate_link_type(llama3_answers)

    as_relationships = parse_as_relationships(file2_path)
    
    # Evaluate asrank inferences
    asrank_results = evaluate_inferences(asrank_inferences, as_relationships)
    print(f"ASRank Inferences - Correct: {asrank_results[1]}, Total: {asrank_results[2]}, Accuracy: {asrank_results[0]:.2f}")
    print(f"In asrank, there are {p2p_asrank} p2p links,{p2c_asrank} p2c links and {s2s_asrank} s2s links.")
    # Evaluate llama3-8b-8192 inferences
    llama3_results = evaluate_inferences(llama3_answers, as_relationships)
    print(f"Llama3-8b-8192 Inferences - Correct: {llama3_results[1]}, Total: {llama3_results[2]}, Accuracy: {llama3_results[0]:.2f}")
    print(f"In llama3, there are {p2p_llama3} p2p links,{p2c_llama3} p2c links and {s2s_llama3} s2s links.")

# # Example usage
# file1_path = 'file1.json'
# file2_path = 'file2.txt'
# main(file1_path, file2_path)


# Example usage with file paths
file1_path = '/home/yyc/BGP-Woodpecker/BGPAgent/program_data/0723/cache/llama3_20190606_case_study_all_question_p2c.json'
file2_path = '/home/yyc/BGP-Woodpecker/asrank_data/relationship_data/20240301.as-rel.txt'
main(file1_path, file2_path)

