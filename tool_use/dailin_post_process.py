import pathlib
from groq import Groq
import os
import pathlib
import json
from tqdm import tqdm
import time
import multiprocessing
os.environ["GROQ_API_KEY"]="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"
keys=[
    "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",
      "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",
      "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",
      "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"
      ]
def generate(idx,content,key):
    #client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
    client = Groq(api_key=key,)
    while True:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role":"system",
                        "content": "You will be given a dialogue with dirty char.You should give me the filtered dialogue.Your output should in json format strictly.You should output the json format directly.the key should be 'conversation','speaker'and 'content'"
                    },
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                model="llama3-70b-8192",
                temperature=1,
                max_tokens=4096
            )
            generation=chat_completion.choices[0].message.content
        except Exception:
            continue
        try:
            json_format=json.loads(generation)
            time.sleep(5)
            break
        except Exception:
            print("error line"+str(idx))
    return json_format

def split_list_into_n_parts(lst, n):
    # 计算每部分的大小
    part_size, extras = divmod(len(lst), n)
    
    # 使用列表推导式和range生成索引，以便切片
    indices = [0] + [part_size * i + min(i, extras) for i in range(1, n + 1)]
    
    # 使用zip和切片来创建子列表
    return [lst[indices[i]:indices[i+1]] for i in range(n)]

def _process(part,key):
    part=tqdm(part)
    for idx,line in enumerate(part):
        with pathlib.Path("./final_qa.json").open('a') as f:
            paper=line['paper']
            input="input dialogue: "+line['answer']
            qa_format=generate(idx=idx,content=input,key=key)
            json.dump({'id':idx,'paper':paper,"qa_pair":qa_format},f)
            f.write('\n')


if __name__ == "__main__":
    all_str=set()
    with pathlib.Path("./filter_pubmed_4o_1.json").open("r") as file:
        lines=file.readlines()
        
    with pathlib.Path("./final_qa.json").open('r') as tf:
        origin=tf.readlines()
        origin=[json.loads(line) for line in origin]
        for o in origin:
            all_str.add(o['paper'])

    #lines=tqdm(lines)
    list_to_split=[]
    for idx,line in enumerate(lines):
        line=json.loads(line)
        paper=line['paper']
        if paper not in all_str:
            list_to_split.append(line)

    with pathlib.Path("./final_qa.json").open('a') as f:
        splited_list=split_list_into_n_parts(list_to_split,4)
        processes = []

        # 创建五个进程并将它们添加到列表中
        for idx in range(4):
            process = multiprocessing.Process(target=_process, args=(splited_list[idx],keys[idx]))
            processes.append(process)
            process.start()  # 启动进程

        # 等待所有进程完成
        for process in processes:
            process.join()
        #process(part=part)
        


