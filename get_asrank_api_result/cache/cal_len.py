import json

with open("20240301_all-paths_cache_asrank.json", "r") as f:
    data = json.load(f)

print(len(data))