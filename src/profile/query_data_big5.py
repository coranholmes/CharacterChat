#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/9/23 3:43 pm
# @Author  : CHEN Weiling
# @File    : query_data_big5.py
# @Software: PyCharm
# @Comments:


import re
import sys
import time
import openai
import json
import threading
import datetime
import os
import argparse
import math
import numpy as np


def get_data(content, mode='', api_key='', max_tries=5):
    n = 0
    USE_MODEL = "gpt-3.5-turbo-16k-0613"
    while n < max_tries:
        try:
            if mode == 'multi':
                openai.api_key = api_key
                USE_MODEL = "gpt-3.5-turbo-16k-0613"  # gpt-3.5-turbo-16k-0613
            response = openai.ChatCompletion.create(
                model=USE_MODEL,
                messages=content
            )
            if USE_MODEL == "gpt-4":
                print("Start waiting for 60s...")
                time.sleep(60)
            break
        except Exception as e:
            print(e)
            n += 1
            print("Retry after {}s".format(n))
            time.sleep(n)
            continue
    if n == max_tries:
        return -1

    return response["choices"][0]["message"]["content"]


def get_profile(content):
    profile = re.findall(r'{.*}', content, re.DOTALL)
    if profile:
        profile = profile[0]
    else:
        profile = ''
    return profile


def thread_query(index, mbti, command_list, api_key, key_n, thread_n, base_path):
    content = []
    profile = ''
    filled_profile = ''
    for i, command in enumerate(command_list):
        input_text = command
        content.append({"role": "user", "content": input_text})
        response = get_data(content, mode='multi', api_key=api_key)
        # response = -1
        if response == -1:
            print("Failed to process: " + input_text[110:150])
            print("response -1 error!!!")
            profile = ''
            filled_profile = ''
        else:
            profile = get_profile(response)
            filled_profile = get_profile(response)

        json_item = {
            'index': int(index[i]),
            'mbti': mbti[i],
            'profile': profile,
            'filled_profile': filled_profile
        }
        with open(base_path + 'key_{}_thread_{}.json'.format(str(key_n), str(thread_n)), 'a',
                  encoding='utf-8') as f:
            f.write(json.dumps(json_item, ensure_ascii=False))
            f.write('\n')
        content.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='./data/profile_input.json')
    parser.add_argument('--output_dir', type=str, default='./data/profile_output/')
    parser.add_argument('--output_file', type=str, default='./data/profile_output.json')
    parser.add_argument('--api_key_file', type=str, default='./api_keys.txt')
    parser.add_argument('--start_from', type=int, default=0)
    parser.add_argument('--thread_num', type=int, default=4)
    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    output_file = args.output_file

    # if output_dir exists, delete it
    if os.path.exists(output_dir):
        os.system('rm -rf ' + output_dir)
    os.makedirs(output_dir)

    with open(args.api_key_file, 'r+', encoding='utf-8') as f:
        api_key_list = [_.strip() for _ in f.readlines()]
    with open(input_file, 'r+', encoding='utf-8') as f:
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
        print("thread_n", thread_n)
        command_list, mbti_list = [], []
        for data in data_list_per_thread[thread_n]:
            mbti_list.append(data['mbti'])
            command_list.append(data['command_list'][0])  # TODO 未测试
        # print("command_list_len", len(command_list))
        t = threading.Thread(target=thread_query, args=(index_list_per_thread[thread_n], mbti_list, command_list, api_key_per_thread[thread_n], 0, thread_n, output_dir))
        thread_list.append(t)
    for t in thread_list:
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()

    file_list = os.listdir(output_dir)
    for file in file_list:
        with open(output_dir+file, 'r+', encoding='utf-8') as fin:
            with open(output_file, 'a', encoding='utf-8') as fout:
                line = fin.readline()
                while line:
                    fout.write(line)
                    line = fin.readline()
