#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/9/23 2:04 pm
# @Author  : CHEN Weiling
# @File    : make_data_big5.py
# @Software: PyCharm
# @Comments:


import json, os, random

input_text = """Here is the brief introduction of the given personality description based on the Big Five personality traits:
@DESCRIPTION@

You are an outstanding creator, you can construct a variety of characters in the real world. Now, based on the given personality type, please design a virtual character according to the following given fields, and you can use your talents as much as possible to boldly Fantasy, but it is necessary to ensure that some attribute information of the characters needs to be distributed diversely, reasonably related, and in line with the laws of nature.

Fill the result into JSON:
{
"name": , # a name. Don't come up with cliché names like Johnny, think carefully about all possible names
"gender": , # male or female. This person could be a man or a woman, so don't be gender biased
"age": , # it can be any age, it is best to randomly select a number between 12 and 80 years old
"region": , # can be any region all over the world
"tone": , # describe in detail the character's idiomatic tone of voice when chatting with others
"job": , # the character's job (fill in "student" if the character is a student). Don't come up with cliché jobs like accountant or freelancer, think carefully and creatively about all possible jobs together with the character's affiliation
"personality": , # a person's personality should be diverse and unified, some extreme and negative personalities are also okay and acceptable in creative writing, everyone is unique
"advantages_and_disadvantages": , # describe in detail the character's strengths and weaknesses
"hobby": , # personal hobbies. It may be a relatively unknown niche hobby, please think about all possible hobbies, even though there are some niche and weird hobbies
"growth_experience": , # the unforgettable memories of this character during the growth process can be several specific and true story experiences, the more detailed the growth experience, the better
"family_relationship": , # the person's family situation
"working_conditions": , # the person's work status. If the person's occupation is a student, fill in the person's study status
"social_relationship": , # the person's social status
"emotional_state": , # the emotional status of this person, usually over the age of 18, there is a high probability of love or marriage relationship
"living_conditions": , # how is this character's life currently
"recent_worry_or_anxiety": # what has this person been feeling anxious or troubled about recently
}

According to the above requirements, start to conceive a unique character image, ensure that the character image is rich, diverse and comprehensive, and do not output other information
"""

fill_prompt = """Expand this virtual character image to make the various attributes of the character more detailed and substantial. You can use your imagination to expand the existing content of the field, or associate some other fields, and output it in a standard parsable JSON format.
Do not output extra information other than JSON.
"""

if __name__ == '__main__':
    root_dir = '/Users/weiling/Codes/CharacterChat'
    big_five_dir = os.path.join(root_dir, 'data')
    with open(os.path.join(big_five_dir, 'big_five_adj.txt'), 'r+', encoding='utf-8') as f:
        adj_list = f.readlines()

    for adjs in adj_list:
        for degree in ['extremely ', 'a bit ']:
            degree_adjs = adjs.strip().split(',')
            degree_adjs = [degree + adj for adj in degree_adjs]

            adj_cnt = len(degree_adjs)
            random.shuffle(degree_adjs)
            # randomly select 2~n adjs
            degree_adjs = degree_adjs[:random.randint(2, adj_cnt)]

            degree_adjs = ", ".join(degree_adjs)
            profile_prompt = input_text
            profile_prompt = profile_prompt.replace('@DESCRIPTION@', degree_adjs)

            json_item = {
                'mbti': degree_adjs,
                'command_list': [profile_prompt, fill_prompt]
            }

            with open(os.path.join(big_five_dir, 'profile_input.json'), 'a', encoding='utf-8') as f:
                f.write(json.dumps(json_item, ensure_ascii=False))
                f.write('\n')