#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 28/9/23 3:07 pm
# @Author  : CHEN Weiling
# @File    : format_profile_input.py
# @Software: PyCharm
# @Comments: 输出profile中包含的job

import json, os, re
import sys

def extract_job(input_string):
    pattern = r'"job":[\s]*([^,]+?),'
    match = re.search(pattern, input_string)
    if match:
        job_value = match.group(1)
        return job_value
    else:
        return None


if __name__ == "__main__":
    root_dir = '/Users/weiling/Codes/CharacterChat'
    big_five_dir = os.path.join(root_dir, 'data')
    profile_path = os.path.join(big_five_dir, 'MBTI/profile_input.json')
    with open(profile_path, 'r', encoding='utf-8') as f:
        data_list = [json.loads(_) for _ in f.readlines()]
    mbti_list = []
    for data in data_list:
        mbti = data['mbti'].strip()
        command_list = data['command_list']
        s = command_list[0].find('JSON:')
        e = command_list[0].find('According to')
        json_str = command_list[0][s+5:e].strip()
        job = extract_job(json_str)
        print(job)
        # s = command_list[0].find('"job"')
        # e = command_list[0].find('"personality"')
        # print(command_list[0][s+7:e].strip())