#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/10/23 3:08 pm
# @Author  : CHEN Weiling
# @File    : build_big5_dic.py
# @Software: PyCharm
# @Comments: 构造big5计分用词典

import json

if __name__ == "__main__":
    extroversion = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    agreeableness = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46]
    conscientiousness = [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]
    neuroticism = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
    openness = [4, 9, 14, 19, 24, 29, 34, 39, 44, 49]
    base_score = [1, -1, 1, -1, 1,
                  -1, 1, -1, 1, -1,
                  1, -1, 1, -1, 1,
                  -1, 1, -1, 1, -1,
                  1, -1, 1, -1, 1,
                  -1, 1, -1, -1, -1,
                  1, -1, 1, -1, 1,
                  -1, 1, -1, -1, 1,
                  1, 1 , 1, -1, 1,
                  -1, 1, 1, -1, 1
                  ]
    big_five = {}
    with open('./data/big5_questions.txt', 'r', encoding='utf-8') as f:
        questions = [_.strip() for _ in f.readlines()]
    for i, question in enumerate(questions):
        key = question
        if i in extroversion:
            type = 'extroversion'
        elif i in agreeableness:
            type = 'agreeableness'
        elif i in conscientiousness:
            type = 'conscientiousness'
        elif i in neuroticism:
            type = 'neuroticism'
        elif i in openness:
            type = 'openness'
        else:
            raise ValueError("i is not in any type")
        big_five[key] = {'type': type, 'score': base_score[i]}
    with open('./data/big5_dic.json', 'w', encoding='utf-8') as f:
        json.dump(big_five, f, ensure_ascii=False)

