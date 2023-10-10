#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 5/10/23 11:11 am
# @Author  : CHEN Weiling
# @File    : build_dataset_fastchat.py
# @Software: PyCharm
# @Comments: covert the llama-et dataset to the format of fastchat

import argparse, json
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='./data/dial_output.json')
    parser.add_argument('--output_file', type=str, default='./data/big5_training_1000_fastchat.json')
    parser.add_argument('--reindex', action='store_true', default=False)
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    reindex = args.reindex

    with open(input_file, 'r') as f:
        data = f.readlines()

    print('Total number of dialogues: {}'.format(len(data)))

    dialogues = []

    for j, dialog in enumerate(data):
        dialog = json.loads(dialog.strip())
        if reindex:
            dialog['index'] = j
        dialogues.append(dialog)

    res = []

    for d in dialogues:
        index = d['index']
        print("Processing dialogue {}...".format(index))
        seeker_info = d['seeker_info']
        supporter_info = d['supporter_info']
        dial = d['dial']
        if len(dial) < 20:
            dial = dial[:-2]  # remove the last two sentences (goodbye)
        elif len(dial) > 20:
            dial = dial[:20]  # only keep the first 20 sentences
        dial = dial[1:-1] # remove the first sentence (hello) from supporter and last sentence from seeker
        row = {}
        row['id'] = index
        row['instruction'] = supporter_info['supporter_statement'] + ' You are ' + supporter_info['supporter_mbti'] + '. You are talking with another person online. The below is your chat history. Please output your response according to your character setting for the following message sent by the other person.'
        row['conversations'] = []
        for j in range(0, len(dial), 2):
            assert dial[j]['speaker'] == 'seeker'  # user's query
            s1 = dial[j]['utterance']
            assert dial[j + 1]['speaker'] == 'supporter'  # model's response
            s2 = dial[j + 1]['utterance']
            row['conversations'].append({'from': 'human', 'value': s1})
            row['conversations'].append({'from': 'gpt', 'value': s2})
        res.append(row)
    print('Total number of dialogues: {}'.format(len(res)))
    with open(output_file, 'w') as f:
        json.dump(res, f, indent=4)
