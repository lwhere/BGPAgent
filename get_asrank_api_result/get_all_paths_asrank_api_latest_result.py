import asyncio
import json
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from tqdm.asyncio import tqdm  # 使用tqdm的asyncio支持版本
from typing import List

# 定义GraphQL查询模板
query_as_latest_information_template = """
{asn(asn:"{as_n}"){
    date
    cliqueMember
    asnDegree {
        transit
    }
    rank
    asnName,
    organization{orgId,orgName},
    asnLinks(first:10){
    totalCount,
    pageInfo{first,offset,status,hasNextPage},
    edges{node{
      asn0{asn,asnName},
      asn1{asn,asnName}
    }
  }
}}}
"""

query_as_latest_few_information_template = """
{asn(asn:"{as_n}"){
    date
    cliqueMember
    asnDegree {
        transit
    }
    rank
    asnName,
    organization{orgId,orgName}
}}
"""

# 创建一个GraphQL客户端
transport = AIOHTTPTransport(url="https://api.asrank.caida.org/v2/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# 缓存字典
asn_cache = {}

# 获取AS最新的信息
async def get_as_latest_information(asn):
    if asn in asn_cache:
        return {"retrived_asn": asn, "as_information": asn_cache[asn]}
    
    query = gql(query_as_latest_information_template.replace("{as_n}", asn))
    try:
        response = await client.execute_async(query)
        asn_cache[asn] = response["asn"]
        return {"retrived_asn": asn, "as_information": response["asn"]}
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"Failed to get as information for ASN {asn}: {e}")
        return None

async def get_as_latest_few_information(asn):
    if asn in asn_cache:
        return {"retrived_asn": asn, "as_information": asn_cache[asn]}
    
    query = gql(query_as_latest_few_information_template.replace("{as_n}", asn))
    try:
        response = await client.execute_async(query)
        asn_cache[asn] = response["asn"]
        return {"retrived_asn": asn, "as_information": response["asn"]}
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"Failed to get as information for ASN {asn}: {e}")
        return None

# 读取JSON文件并提取AS列表
def read_as_numbers(input_path):
    with open(input_path, "r") as file:
        data = json.load(file)
    as_numbers = set()
    for entry in data:
        as_path = entry.get("as_path", "")
        as_numbers.update(as_path.split("|"))
    return as_numbers

def read_as_numbers_from_path(as_path):
    as_numbers = set()
    as_numbers.update(as_path.split("|"))
    return as_numbers

async def get_as_information_from_as_path(as_path: str):
    as_numbers = read_as_numbers_from_path(as_path)
    as_information_list = []

    for asn in tqdm(as_numbers):
        as_information = await get_as_latest_few_information(asn)
        if as_information is not None:
            as_information_list.append(as_information)

    return as_information_list

async def get_as_information_from_as_members(as_members: set):
    as_information_list = []

    for asn in tqdm(as_members):
        as_information = await get_as_latest_few_information(asn)
        if as_information is not None:
            as_information_list.append(as_information)

    return as_information_list

def process_line(line):
    parts = line.split()
    item = {
        "time": "2023-03-01",
        "organization running the collector": parts[0].split('/')[0],
        "name of BGPstream collector": parts[0].split('/')[1],
        "frequency of observations": parts[0].split('|')[1],
        "as_path": parts[1],
        "prefix": parts[2],
        "code": parts[3],
        "peer_ip": parts[4]
    }
    return item

def count_lines(file_path):
    with open(file_path, 'r') as file:
        for i, _ in enumerate(file):
            pass
    return i + 1

def process_file(file_path, cache_path):
    result = []
    cache_count = 0
    cache_size = 100
    total_lines = count_lines(file_path)

    with open(file_path, 'r') as file, tqdm(total=total_lines) as pbar:
        for line in file:
            processed_item = process_line(line)
            as_path = processed_item["as_path"]
            as_members = read_as_numbers_from_path(as_path)
            ases_information_api = asyncio.run(get_as_information_from_as_members(as_members))
            result.append(ases_information_api)
            cache_count += 1

            if cache_count == cache_size:
                with open(cache_path, 'a') as cache:
                    json.dump(result, cache, indent=4)
                    cache.write('\n')
                result.clear()
                cache_count = 0

            pbar.update(1)

    # Write any remaining items to the cache file
    if result:
        with open(cache_path, 'a') as cache:
            json.dump(result, cache, indent=4)
            cache.write('\n')

# 运行主函数
if __name__ == "__main__":
    # Example usage
    file_path = '/home/yyc/BGP-Woodpecker/asrank_data/20240301.all-paths'
    cache_path = './cache/20240301_all-paths_cache_asrank.json'
    process_file(file_path, cache_path)