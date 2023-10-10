#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 26/9/23 10:07 am
# @Author  : CHEN Weiling
# @File    : query_data_big5.py
# @Software: PyCharm
# @Comments:


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
import ast


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

def get_sns(profile, api_key):
    prompt = """The following is a description of a personal profile (JSON format):
@DESCRIPTION@

You are an outstanding creator, generate a list of 20 different Facebook status updates as this person. 
Each update must be verbose and reflect the person’s personality and description. 
The updates should cover, but should not be limited to, the following topics: work, social relationships, free time, personal concerns, hobbies, and communication with others. 
The updates should be written in the first person, as if the person is writing them.

Fill the result into a list, each status must be quoted with double quotation marks and separated by comma, for example:
["1st status", "2nd status", ..., "20th status"]
"""

    prompt = prompt.replace('@DESCRIPTION@', str(profile))
    content = [{'role': 'user', 'content': prompt}]
    additional_information = get_data(content, mode='multi', api_key=api_key)
    if additional_information == -1:
        additional_information = ''
    return additional_information


def cheeck_sns(sns):
    if not sns.startswith('[') or not sns.endswith(']'):
        return False
    if sns[-2] == ',':
        return False
    if sns.count('[') > 2:
        return False
    if sns.count('",') < 20:
        return False
    return True

def thread_query(index, mbti, profile_list, api_key, key_n, thread_n, base_path):
    for i, profile in enumerate(profile_list):
        # print("thread_n ", thread_n, " index", i, "is processing:", mbti[i])
        data = {}
        data['index'] = index[i]
        data['mbti'] = mbti[i]
        data['profile_trans'] = profile
        sns = ''
        retry_cnt = 0
        while cheeck_sns(sns) == False:
            sns = get_sns(profile, api_key)
            retry_cnt += 1
            if retry_cnt > 5:
                print("Error: ====================================", mbti[i])
                print(sns)
                continue
        try:
            sns = json.loads(sns)  # Safely evaluate the string as a list
        except:
            print("Error: ====================================", mbti[i])
            print(sns)
            continue
        data['sns'] = sns
        # convert sns from a string to a list
        with open(base_path + 'key_{}_thread_{}.json'.format(str(key_n), str(thread_n)), 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
            f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='./data/profile_trans_output.json')
    parser.add_argument('--output_dir', type=str, default='./data/sns_output/')
    parser.add_argument('--output_file', type=str, default='./data/sns_output.json')
    parser.add_argument('--api_key_file', type=str, default='./api_keys.txt')
    parser.add_argument('--thread_num', type=int, default=4)
    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    output_file = args.output_file

    # if output_dir exists, delete it
    if os.path.exists(output_dir):
        os.system('rm -rf ' + output_dir)
    os.makedirs(output_dir)
    if os.path.exists(output_file):
        os.system('rm ' + output_file)

    with open(args.api_key_file, 'r+', encoding='utf-8') as f:
        api_key_list = [_.strip() for _ in f.readlines()]
    with open(input_file, 'r+', encoding='utf-8') as f:
        data_list = [json.loads(_) for _ in f.readlines()]

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
        profile, mbti_list = [], []
        for data in data_list_per_thread[thread_n]:
            mbti_list.append(data['mbti'])
            profile.append(data['profile_trans'])
        t = threading.Thread(target=thread_query, args=(index_list_per_thread[thread_n], mbti_list, profile, api_key_per_thread[thread_n], 0, thread_n, output_dir))
        thread_list.append(t)
    for t in thread_list:
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()

    file_list = os.listdir(output_dir)
    for file in file_list:
        with open(output_dir + file, 'r+', encoding='utf-8') as fin:
            with open(output_file, 'a', encoding='utf-8') as fout:
                line = fin.readline()
                while line:
                    fout.write(line)
                    line = fin.readline()