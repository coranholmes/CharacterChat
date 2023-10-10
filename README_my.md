## 运行流程
1. 生成profile(GPT-4): `./src/gen_profile.sh`
2. 转写profile(GPT-3.5): `./src/gen_profile_trans.sh`
3. 生成对话(GPT-3.5): `./src/gen_dial.sh`
4. 用llama-efficient-tuning进行训练
5. 用llama-efficient-tuning进行性格测试获取response
5. 评测response(GPT-3.5): `./src/gen_personality_rating.py`(包括①根据response生成每一题的打分，②计算大五人格各项分数)

## 生成SNS帖子
1. 根据profile生成SNS帖子: `python src/sns/query_data_big5.py --thread_num 4`