## 数据文件夹一览

| 文件/文件夹                        | 内容                                          |
|-------------------------------|---------------------------------------------|
| gpt-3.5_big5_consulting       | 使用CharacterChat原有prompt生成咨询场景的对话（已废弃）       |
| gpt4-profile-35-dial_v1       | gpt4生成profile之后，gpt3.5生成对话（任意话题）            |
| * gpt4-profile-35-dial-1000 * | gpt4生成profile之后，gpt3.5生成对话（任意话题），1000条数据最终版 |
| big5_dic.json                 | big5计分词典                                    |
| big5_questions.txt            | big5测评50题                                   |
|big_five_adj.txt| big5各类性格形容词                                 |

## 训练数据相关
主要文件夹 gpt4-profile-35-dial-1000

| 文件/文件夹                                 | 内容                                             |
|----------------------------------------|------------------------------------------------|
| big5_IPIP_50item_rating_new_template   | 针对模型response给出的rating（每条训练数据使用不同system prompt） |
| big5_IPIP_50item_response_new_template | 模型response                                     |
| big5_rating.json                       | gpt3.5给出的rating（每条训练数据使用不同system prompt）       |
| training/big5_training_1000.json       | 使用相同system prompt的旧模板数据（已废弃）                   |
| training/big5_training_1000_v2.json    | 使用不同system prompt的新模板数据（最终版）                   |
| training/big5_training_fastchat.json   | 使用不同system prompt的新模板数据（fastchat版）             |
