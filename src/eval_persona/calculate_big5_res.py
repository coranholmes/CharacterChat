#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/10/23 2:37 pm
# @Author  : CHEN Weiling
# @File    : calculate_big5_res.py
# @Software: PyCharm
# @Comments: 根据问卷回答，计算大五人格分数


import os, argparse, json, re

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='')
    parser.add_argument('--input_dir', type=str, default='./data/gpt4-profile-35-dial-1000/big5_rating/big5_IPIP_50item_rating_new_template/')
    parser.add_argument('--output_file', type=str, default='./data/gpt4-profile-35-dial-1000/big5_rating/big5_rating_v2.json')
    parser.add_argument('--api_key_file', type=str, default='./api_keys.txt')
    parser.add_argument('--start_from', type=int, default=0)
    parser.add_argument('--thread_num', type=int, default=4)
    args = parser.parse_args()

    output_file = args.output_file
    big5_dic_file = './data/big5_dic.json'
    input_dir = args.input_dir
    input_file = args.input_file

    if input_dir != '':
        file_list = os.listdir(input_dir)
    elif input_file != '':
        file_list = [input_file]
    else:
        raise ValueError("input_dir or input_file must be specified")

    with open(big5_dic_file, 'r+', encoding='utf-8') as f:
        big5_dic = json.load(f)

    # for input_file in file_list:
    for i in range(len(file_list)):
        input_file = 'eval_persona_' + str(i) + '_output.json'
        scores = {
            'extroversion': 20,
            'agreeableness': 14,
            'conscientiousness': 14,
            'neuroticism': 38,
            'openness': 8
        }
        print("input_file: ", input_file)
        with open(input_dir + input_file, 'r+', encoding='utf-8') as f:
            data_list = [json.loads(_) for _ in f.readlines()]
        for data in data_list:
            try:
                rating = json.loads(data["rating"])
                score = int(rating["rating"])
            except:
                print("Q:{}\tA:{}".format(data['question'], data['response']))
                print(data["rating"])
                # extract score from rating
                score = int(re.findall(r'\d+', data["rating"])[0])
                print(score)

            question = data['question']
            type = big5_dic[question]['type']
            scores[type] += score * big5_dic[question]['score']
        scores["mbti"] = data["mbti"]
        scores["index"] = data["index"]
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(scores, ensure_ascii=False))
            f.write('\n')