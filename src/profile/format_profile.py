#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/9/23 5:00 pm
# @Author  : CHEN Weiling
# @File    : format_profile.py
# @Software: PyCharm
# @Comments: 打印输出格式化的profile

import json, os
import sys

if __name__ == "__main__":
    root_dir = '/Users/weiling/Codes/CharacterChat'
    big_five_dir = os.path.join(root_dir, 'data')
    # profile_path = os.path.join(big_five_dir, 'gpt4-profile-3.5-dial_v1/profile_output_gpt4.json')
    # profile_path = os.path.join(big_five_dir, 'profile_output.json')
    profile_path = os.path.join(big_five_dir, 'MBTI/profile_output.json')
    with open(profile_path, 'r', encoding='utf-8') as f:
        data_list = [json.loads(_) for _ in f.readlines()]
    mbti_list = []
    for data in data_list:
        mbti = data['mbti'].strip()
        if "MBTI" in profile_path:
            if mbti not in mbti_list:
                print(mbti, ":\t", data['profile']['job'])
                # print("=====================================")
        else:
            # mbti = mbti.split(',')[0]
            if data['profile'] == '':
                print(mbti, ":\t", "No profile！！！！！！！！！！！！！！！")
                continue
            profile = json.loads(data['profile'])
            print(mbti, ":\t", profile['job'])
            # print("=====================================")
