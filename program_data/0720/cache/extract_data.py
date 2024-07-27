import json

with open("extracted_data.json", "r") as f:
    data = json.load(f)
# Function to format data into Alpaca format
def format_to_alpaca(data):
    formatted_data = []
    for item in data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        question = question.replace("{'question': '", "").replace("。'}.", ":").replace(" 为 ", "为")
        instrution = "Please use the given as path to infer business relationships: "
        as_path = question.split("as path为")[1]
        formatted_data.append({
            "instruction": instrution+as_path,
            "input": "",
            "output": answer
        })
    return formatted_data

# Format the data
alpaca_data = format_to_alpaca(data)

# Save the formatted data to a JSON file
with open('alpaca_formatted_data.json', 'w', encoding='utf-8') as f:
    json.dump(alpaca_data, f, ensure_ascii=False, indent=4)

print("Data has been formatted and saved to alpaca_formatted_data.json")