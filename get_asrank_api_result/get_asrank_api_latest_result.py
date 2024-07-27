import asyncio
import json
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from tqdm.asyncio import tqdm  # 使用tqdm的asyncio支持版本

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

# 创建一个GraphQL客户端
transport = AIOHTTPTransport(url="https://api.asrank.caida.org/v2/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# 获取AS最新的信息


async def get_as_latest_information(asn):
    query = gql(query_as_latest_information_template.replace("{as_n}", asn))
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

def read_as_numbers_from_paths(as_paths):
    as_numbers = set()
    for as_path in as_paths:
        as_numbers.update(as_path.split("|"))
    return as_numbers

# 处理主函数


async def main(input_path):
    as_numbers = read_as_numbers(input_path)
    as_information_list = []

    for asn in tqdm(as_numbers):
        as_information = await get_as_latest_information(asn)
        if as_information is not None:
            as_information_list.append(as_information)
        output_path = "./cache/cache_all_paths_cached_as_information.json"
        # 将数据写入到JSON文件中
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(as_information_list, json_file, ensure_ascii=False, indent=4)

    return as_information_list


# 运行主函数
if __name__ == "__main__":
    # 运行完filter脚本得到的json结果
    input_path = "/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20190606_case_study_aspath.json"
    as_information_list = asyncio.run(main(input_path))
    output_path = "/home/yyc/BGP-Woodpecker/asrank_data/20190606_case_study_aspath_asrank_api_latest_result.json"
    # 将数据写入到JSON文件中
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(as_information_list, json_file, ensure_ascii=False, indent=4)
