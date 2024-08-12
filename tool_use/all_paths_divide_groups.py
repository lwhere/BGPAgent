import json

# Function to process data in chunks and save to a file
def process_and_save_data(input_file, output_file):
    with open(input_file, 'r') as file:
        data = file.readlines()

    output_data = []
    temp_data = {}
    count = 1
    for i, line in enumerate(data):
        entry = json.loads(line)
        as_path = entry.get("as_path", "")
        temp_data[f"number{count}"] = as_path
        count += 1
        
        # Every 10 entries, save the group and reset
        if (i + 1) % 20 == 0 or (i + 1) == len(data):
            output_data.append(temp_data)
            temp_data = {}
            count = 1

    # Save the output to a file
    with open(output_file, 'w+') as file:
        json.dump(output_data, file, indent=4)

# Example usage
input_file = '/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20240301_all-paths_cache_top_5000.json'
output_file = '/home/yyc/BGP-Woodpecker/BGPAgent/tool_use/20240301_all-paths_20paths.json'
process_and_save_data(input_file, output_file)
