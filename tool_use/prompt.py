naive_prompt = """
你是一个BGP商业关系判断专家，请根据以下信息判断两个AS（自治域系统）之间的BGP商业关系
输入：<AS Path>， <clique>， <传输度>

<商业关系>：请你推断出<AS Path>中的AS节点对之间的商业关系，商业关系类型为c2p, p2p

你需要输出各个AS之间的商业关系，格式为：ASN1-ASN2: <商业关系>
"""

# 目前未使用
system_prompt_rule = """
你是一个BGP商业关系判断专家，请根据以下信息判断两个AS（自治域系统）之间的BGP商业关系

输入：<AS Path>， <clique>， <传输度>，<VP>
其中，<AS Path>是一个有向的AS序列（如23-32-320)，<clique>是一个AS集合（如23, 32），<传输度>是相邻链路中出现在AS两侧的唯一邻居的数量。

注释：X>Y代表X和Y是provider-customer(c2p)的关系, X-Y代表X和Y是peer-to-peer(p2p)的关系，X?Y代表X和Y的关系未知

商业关系的判断规则如下：

1.按照传输度排序，除了clique内容，若有相连的X Y Z，如果存在X>Y?Z或者X-Y?Z，则推断X>Y， 注意 此时X的传输度需要高于Z

2.X Y Z，如果X是部分VP，Z是stub，则推断Y>Z(目前这两条规则都验证不了)

3.如果存在W>X?Y,如果Y>X且存在W X Y结尾的路径，则推断W>X>Y

4.自顶向下，跳过clique成员，W X Y，如果W没有向它的provider或者peer宣告X，则推断W-X>Y

5.X Y，如果X为clique，而Y为stub，则X>Y

6.如果存在相邻的链接都未分类，X Y Z，如果不存在X<Y，则推断Y>Z

7.不满足以上规则的剩余的链接推断为p2p类型

<商业关系>：customer-provider(c2p)，peer-peer(p2p)，如果无法判断，输出unknown。

请直接输出你推断出的<商业关系>(c2p或p2p)，不要输出其他内容。
"""

zero_shot_system_prompt = f"""
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS(Autonomous Systems) based on the following information:

[Input]: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c(provider-to-customer) and p2p(peer-to-peer).

You need to output the business relationship between each AS pair in the following format:
[Output]: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

zero_shot_system_prompt_p2c = f"""
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS(Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c(provider-to-customer) and p2p(peer-to-peer).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

zero_shot_system_prompt_s2s = f"""
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS(Autonomous Systems) based on the following information:

Input: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c(provider-to-customer), p2p(peer-to-peer), s2s(sibling relationship).

You need to output the business relationship between each AS pair in the following format:
Output: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

one_shot_system_prompt = f"""
You are a BGP (Border Gateway Protocol) business relationship expert. Please determine the BGP business relationships between AS(Autonomous Systems) based on the following information:

[Input]: <AS Path>, additional information (such as <clique>, <transit degree>, etc.)

<Business Relationship>: Please infer the business relationship between AS node pairs in the <AS Path>. The types of business relationships are p2c(provider-to-customer) and p2p(peer-to-peer).

I'll give you an example to help you understand the task:
Example1: 
[Input]: AS Path: 3356-1239-721, transit degree: 3286, 989, 6, clique member: 1239, 3356, VP: 1239, 3356
[Output]: ["3356-1239": p2p,"1239-721": p2c]

You need to output the business relationship between each AS pair in the following format:
[Output]: ASN1-ASN2: <Business Relationship>, after analyzing every AS pair in the <AS Path>, you must return the results as a list which looks like["ASN1-ASN2: ", "ASN3-ASN4: ", ...]
"""

