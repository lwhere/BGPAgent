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
# 缓存字典
asn_cache = {}

# 创建一个GraphQL客户端
transport = AIOHTTPTransport(url="https://api.asrank.caida.org/v2/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# 获取AS最新的信息
async def get_as_latest_information(asn):
    if asn in asn_cache:
        return {"retrived_asn": asn, "as_information": asn_cache[asn]}
    
    query = gql(query_as_latest_information_template.replace("{as_n}", asn))
    try:
        response = await client.execute_async(query)
        return {"retrived_asn": asn, "as_information": response["asn"]}
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"Failed to get as information for ASN {asn}: {e}")
        return None


async def get_as_latest_few_information(asn):
    if asn in asn_cache:
        return {"retrived_asn": asn, "as_information": asn_cache[asn]}
    
    query = gql(
        query_as_latest_few_information_template.replace("{as_n}", asn))
    try:
        response = await client.execute_async(query)
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


def read_as_numbers_from_path(as_paths):
    as_numbers = set()
    as_numbers.update(as_paths.split("|"))
    return as_numbers

# 处理主函数


async def main(input_path):
    as_numbers = read_as_numbers(input_path)
    as_information_list = []

    for asn in tqdm(as_numbers):
        as_information = await get_as_latest_information(asn)
        if as_information is not None:
            as_information_list.append(as_information)
        output_path = "./cache/cache.json"
        # 将数据写入到JSON文件中
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(as_information_list, json_file,
                      ensure_ascii=False, indent=4)

    return as_information_list


async def get_as_information_from_as_path(as_path: str):
    as_numbers = read_as_numbers_from_path(as_path)
    as_information_list = []

    for asn in tqdm(as_numbers):
        as_information = await get_as_latest_few_information(asn)
        if as_information is not None:
            as_information_list.append(as_information)

    return as_information_list


async def get_as_information_from_as_paths(as_paths: List[str]):
    as_information_list = []

    for as_path in as_paths:
        as_information_list += await get_as_information_from_as_path(as_path)

    return as_information_list

# 运行主函数
if __name__ == "__main__":
    # 运行完filter脚本得到的json结果
    input_path = "/Users/hugo/Projects/NLBGP/BGPAgent/filtered_data/bgpleak_filtered.json"
    as_information_list = asyncio.run(main(input_path))
    output_path = "/Users/hugo/Projects/NLBGP/BGPAgent/filtered_data/bgpleak_filtered_as_information_latest_result.json"
    # 将数据写入到JSON文件中
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(as_information_list, json_file, ensure_ascii=False, indent=4)
