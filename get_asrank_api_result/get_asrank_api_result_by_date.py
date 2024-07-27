import asyncio
import json
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from tqdm.asyncio import tqdm  # 使用tqdm的asyncio支持版本

# 定义GraphQL查询模板
query_as_latest_information_template = """
{
   asns(asns:["{as_n}"], dateStart:"{date_first_day}", dateEnd:"{date}"){
   edges {
     node {
       asn
       rank
       date
      cliqueMember
      asnDegree{
        transit
      }
      organization{
        orgId, orgName
      }
     }
   }
  }
}

"""

# 创建一个GraphQL客户端
transport = AIOHTTPTransport(url="https://api.asrank.caida.org/v2/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# 获取AS最新的信息


async def get_as_latest_information(asn, date):
    query_string = query_as_latest_information_template.replace("{as_n}", asn).replace("{date}", date).replace("\n", "")
    date_first_day = date[:8] + "01"
    query_string = query_string.replace("{date_first_day}", date_first_day)
    query = gql(query_string)
    try:
        response = await client.execute_async(query)
        return {"retrived_asn": asn, "as_information": response["asns"]["edges"][0]["node"]}
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


async def main(input_path, date):
    as_numbers = read_as_numbers(input_path)
    as_information_list = []

    for asn in tqdm(as_numbers):
        as_information = await get_as_latest_information(asn, date)
        if as_information is not None:
            as_information_list.append(as_information)
        name = input_path.split("/")[-1].split(".")[0]
        output_path = f"./cache/cache_by_date_{name}_cached_as_information.json"
        # 将数据写入到JSON文件中
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(as_information_list, json_file, ensure_ascii=False, indent=4)

    return as_information_list


# 运行主函数
if __name__ == "__main__":
    # 运行完filter脚本得到的json结果
    # input_path = "/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20190606_case_study_aspath.json"
    input_path = "/home/yyc/BGP-Woodpecker/BGPAgent/filtered_data/20121105_case_study_aspath.json"
    date = "2012-11-05"
    as_information_list = asyncio.run(main(input_path, date))
    name = input_path.split("/")[-1].split(".")[0]
    output_path = f"/home/yyc/BGP-Woodpecker/asrank_data/{name}_asrank_api_result.json"
    # 将数据写入到JSON文件中
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(as_information_list, json_file, ensure_ascii=False, indent=4)
