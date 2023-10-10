#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/10/23 1:42 pm
# @Author  : CHEN Weiling
# @File    : build_dataset_v2.py
# @Software: PyCharm
# @Comments:
import argparse, json
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='./data/dial_output.json')
    parser.add_argument('--output_file', type=str, default='./data/big_five_v2.json')
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

    with open(output_file, 'w') as f:
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
            row['system'] = 'You are a role playing master and always answer according to your character setting. You don\'t need to be polite, respectful or honest as everyone is different. You just need to stick to your character setting described as follow: ' + supporter_info['supporter_statement'] + ' You are ' + supporter_info['supporter_mbti'] + '. You are talking with another person online. The below is your chat history. Please output your response according to your character setting for the following message sent by the other person.'
            row['input'] = ''
            row['history'] = []
            for j in range(0, len(dial), 2):
                assert dial[j]['speaker'] == 'seeker'  # user's query
                s1 = dial[j]['utterance']
                # if j + 1 < len(dial):
                assert dial[j + 1]['speaker'] == 'supporter'  # model's response
                s2 = dial[j + 1]['utterance']
                if j + 1 == len(dial) - 1:  # 处理最后一组(seeker, supporter)对话
                    row['instruction'] = s1
                    row['output'] = s2
                    continue
                row['history'].append([s1, s2])
            f.write(json.dumps(row) + '\n')
