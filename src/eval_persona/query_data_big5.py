#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/10/23 10:02 am
# @Author  : CHEN Weiling
# @File    : query_data.py
# @Software: PyCharm
# @Comments: 根据问卷回答，查询对应的评分


import os
import math
import sys
import time
import openai
import json
import threading
import datetime
import argparse
import numpy as np


def get_data(content, mode='', api_key='', max_tries=5):
    n = 0
    while n < max_tries:
        try:
            if mode == 'multi':
                openai.api_key = api_key
                USE_MODEL = "gpt-3.5-turbo-16k-0613"
            response = openai.ChatCompletion.create(
                model=USE_MODEL,
                messages=content
            )
            break
        except Exception as e:
            print(e)
            n += 1
            time.sleep(n)
            continue
    if n == max_tries:
        return -1

    return response["choices"][0]["message"]["content"]

def get_rating(question, response, api_key):
    prompt = """You are an experienced counselor and psychologist. You can analyze the personality according to the given response to certain statements. For the statement
"I @Q@", the response is "@A@". Please think carefully and analyze to what extent the person agrees with the statement.

Fill the result into JSON:
{
"rating": # give a score from 1 to 5 (where 1 = "Disagree", 2 ="Slightly disagree", 3 = "Neutral",4 = "Slightly agree", and 5 = "Agree")
"reason": # explain why you give this score, less than 100 words
}
    """

    prompt = prompt.replace('@Q@', question)
    prompt = prompt.replace('@A@', response)
    content = [{'role': 'user', 'content': prompt}]
    additional_information = get_data(content, mode='multi', api_key=api_key)
    if additional_information == -1:
        additional_information = ''
    return additional_information


def thread_query(index, mbti_list, ques_list, res_list, api_key, key_n, thread_n, base_path):
    for i, response in enumerate(res_list):
        print("thread_n ", thread_n, " index", i, "is processing:", mbti_list[i])
        data = {}
        data['index'] = int(index[i])
        data['mbti'] = mbti_list[i]
        data['question'] = ques_list[i]
        data['response'] = response
        data['rating'] = get_rating(data['question'], response, api_key)
        with open(base_path + 'key_{}_thread_{}.json'.format(str(key_n), str(thread_n)), 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
            f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='./data/gpt4-profile-35-dial-1000/big5_rating/big5_IPIP_50item_response_new_template/')
    parser.add_argument('--input_file', type=str, default='')
    parser.add_argument('--output_dir', type=str, default='./data/eval_persona/')
    parser.add_argument('--api_key_file', type=str, default='./api_keys.txt')
    parser.add_argument('--start_from', type=int, default=0)
    parser.add_argument('--thread_num', type=int, default=4)
    args = parser.parse_args()

    input_dir = args.input_dir
    input_file = args.input_file
    output_dir = args.output_dir

    if input_dir != '':
        file_list = os.listdir(input_dir)
    elif input_file != '':
        file_list = [input_file]
    else:
        raise ValueError("input_dir or input_file must be specified")

    # 遍历每个人的问卷
    for input_file in file_list:
        print("input_file: ", input_file)
        # if output_dir exists, delete it
        if os.path.exists(output_dir):
            os.system('rm -rf ' + output_dir)
        os.makedirs(output_dir)

        with open(args.api_key_file, 'r+', encoding='utf-8') as f:
            api_key_list = [_.strip() for _ in f.readlines()]
        with open(input_dir + input_file, 'r+', encoding='utf-8') as f:
            data_list = [json.loads(_) for _ in f.readlines()]

        data_list = data_list[args.start_from:]

        use_key_num = len(api_key_list)
        thread_num = args.thread_num

        # assign data in data_list to each process
        data_num = len(data_list)
        data_per_thread = math.ceil(data_num / thread_num)
        data_list_per_thread = []
        index_list_per_thread = []
        for i in range(thread_num):
            cur_task_ids = np.arange(i, data_num, thread_num)
            index_list_per_thread.append(cur_task_ids)
            data_list_per_thread.append([data_list[_] for _ in cur_task_ids])

        # assign api key to each thread
        api_key_per_thread = []
        for i in range(thread_num):
            api_key_per_thread.append(api_key_list[i % use_key_num])
        # print("api_key_per_thread", api_key_per_thread)

        # for each thread, run thread_query
        thread_list = []
        for thread_n in range(thread_num):
            ques_list, res_list, id_list, mbti_list = [], [], [], []
            for data in data_list_per_thread[thread_n]:
                id_list.append(data['index'])
                mbti_list.append(data['mbti'])
                res_list.append(data['response'])
                ques_list.append(data['question'])
            t = threading.Thread(target=thread_query, args=(id_list, mbti_list, ques_list, res_list, api_key_per_thread[thread_n], 0, thread_n, output_dir))
            thread_list.append(t)
        for t in thread_list:
            t.daemon=True
            t.start()
        for t in thread_list:
            t.join()

        # combine all files
        output_file = "./data/gpt4-profile-35-dial-1000/big5_rating/big5_IPIP_50item_rating_new_template/" + input_file.split('/')[-1].split('.')[0] + "_output.json"
        combined_file_list = os.listdir(output_dir)
        for file in combined_file_list:
            with open(output_dir + file, 'r+', encoding='utf-8') as fin:
                print("Saving file: ", output_dir + file)
                with open(output_file, 'a', encoding='utf-8') as fout:
                    line = fin.readline()
                    while line:
                        fout.write(line)
                        line = fin.readline()