from typing import Literal
from itertools import chain
from transformers import Seq2SeqTrainingArguments
from transformers.tokenization_utils import PreTrainedTokenizer

from datasets import Dataset

from llmtuner.extras.constants import IGNORE_INDEX
from llmtuner.extras.template import get_template
from llmtuner.hparams import DataArguments


def preprocess_dataset(
    dataset: Dataset,
    tokenizer: PreTrainedTokenizer,
    data_args: DataArguments,
    training_args: Seq2SeqTrainingArguments,
    stage: Literal["pt", "sft", "rm", "ppo"]
) -> Dataset:

    column_names = list(dataset.column_names)
    prompt_template = get_template(data_args.prompt_template)

    # support question with a single answer or multiple answers
    def get_dialog(examples):
        for i in range(len(examples["prompt"])):
            if examples["prompt"][i] and examples["response"][i]:
                query, answer = examples["prompt"][i], examples["response"][i]
                query = query + "\n" + examples["query"][i] if examples["query"][i] else query
                prefix = examples["prefix"][i] if examples["prefix"][i] else ""
                dialog = prompt_template.get_dialog(query, answer, examples["history"][i], prefix)
                yield dialog

    def preprocess_pretrain_dataset(examples):
        # build grouped texts with format `<bos> X1 X2 X3 ...` (without <eos>)
        text_ids = tokenizer(examples["prompt"], add_special_tokens=False)["input_ids"]
        concatenated_ids = list(chain(*text_ids))
        total_length = len(concatenated_ids)
        block_size = data_args.max_source_length - 1
        # we drop the small remainder, and if the total_length < block_size, we exclude this batch
        total_length = (total_length // block_size) * block_size
        # split by chunks of max_source_length
        result = [[tokenizer.bos_token_id] + concatenated_ids[i: i + block_size]
                  for i in range(0, total_length, block_size)]
        return {
            "input_ids": result,
            "labels": result.copy()
        }
    
    def format_input(text):
        return "<SEEKER>%s<SUPPORTER>" % text
        # return "<HUMAN>%s<ASSISTANT>" % text  
    
    def format_system(supporter):
        return "<SYSTEM>%s" % supporter
    
    def format_info(character, info):
        return "<%s>[INFO-%s]" % (character, info)
    
    def format_seeker(seeker):
        return "<SEEKER>%s" % seeker
    
    def format_supporter(supporter):
        return "<SUPPORTER>%s" % supporter
    
    def preprocess_model_base_dataset(examples):
        model_inputs = {"input_ids": [], "labels": []}
        
        max_length = 2048
        for example in examples["conversations"]:
            input_ids, labels = [], []

            for turn in example:
                if turn["from"] == "seeker":
                    value_ids = tokenizer.encode(text=format_input(turn['value']), add_special_tokens=False)
                    input_ids += value_ids
                    labels += value_ids
                else:
                    value_ids = tokenizer.encode(text=turn['value'], add_special_tokens=False)
                    input_ids += value_ids + [tokenizer.eos_token_id]
                    labels += value_ids + [tokenizer.eos_token_id]

            if len(input_ids) > max_length:
                input_ids = input_ids[:max_length]
                labels = labels[:max_length]

            model_inputs["input_ids"].append(input_ids)
            model_inputs["labels"].append(labels)

        return model_inputs
    
    def preprocess_model_supporter_dataset(examples):
        model_inputs = {"input_ids": [], "labels": []}
        
        max_length = 2048

        for example in examples["conversations"]:
            input_ids, labels = [], []

            supporter_system = example['system']['supporter']
            dials = example['history']
            info = example['info']
            utterance = example['utterance']

            system = format_system(supporter_system)
            value_ids = tokenizer.encode(text=system, add_special_tokens=False)
            input_ids += value_ids
            labels += [IGNORE_INDEX] * len(value_ids)

            for turn in dials:
                if turn['from'] == 'seeker':
                    cur_input = format_seeker(turn['value'])
                else:
                    cur_input = format_supporter(turn['value'])
                value_ids = tokenizer.encode(text=cur_input, add_special_tokens=False)
                input_ids += value_ids
                labels += [IGNORE_INDEX] * len(value_ids)
            
            info = format_info('SUPPORTER', info)
            value_ids = tokenizer.encode(text=info, add_special_tokens=False)
            input_ids += value_ids
            labels += [IGNORE_INDEX] * len(value_ids)

            value_ids = tokenizer.encode(text=utterance, add_special_tokens=False)
            input_ids += value_ids + [tokenizer.eos_token_id]
            labels += value_ids + [tokenizer.eos_token_id]

            if len(input_ids) > max_length:
                input_ids = input_ids[:max_length]
                labels = labels[:max_length]

            model_inputs["input_ids"].append(input_ids)
            model_inputs["labels"].append(labels)

        return model_inputs
    
    def preprocess_model_seeker_dataset(examples):
        model_inputs = {"input_ids": [], "labels": []}
        
        max_length = 2048

        for example in examples["conversations"]:
            input_ids, labels = [], []

            seeker_system = example['system']['seeker']
            dials = example['history']
            info = example['info']
            utterance = example['utterance']

            system = format_system(seeker_system)
            value_ids = tokenizer.encode(text=system, add_special_tokens=False)
            input_ids += value_ids
            labels += [IGNORE_INDEX] * len(value_ids)

            for turn in dials:
                if turn['from'] == 'seeker':
                    cur_input = format_seeker(turn['value'])
                else:
                    cur_input = format_supporter(turn['value'])
                value_ids = tokenizer.encode(text=cur_input, add_special_tokens=False)
                input_ids += value_ids
                labels += [IGNORE_INDEX] * len(value_ids)
            
            info = format_info('SUPPORTER', info)
            value_ids = tokenizer.encode(text=info, add_special_tokens=False)
            input_ids += value_ids
            labels += [IGNORE_INDEX] * len(value_ids)

            value_ids = tokenizer.encode(text=utterance, add_special_tokens=False)
            input_ids += value_ids + [tokenizer.eos_token_id]
            labels += value_ids + [tokenizer.eos_token_id]

            if len(input_ids) > max_length:
                input_ids = input_ids[:max_length]
                labels = labels[:max_length]

            model_inputs["input_ids"].append(input_ids)
            model_inputs["labels"].append(labels)

        return model_inputs
    
    def preprocess_supervised_dataset(examples):
        # build inputs with format `<bos> X Y <eos>` and labels with format `<ignore> ... <ignore> Y <eos>`
        # for input with history, we build multiple input-label pairs just like:
        # https://github.com/lm-sys/FastChat/blob/f17c092f64840fa6354ed52789dccb2daa793d0b/fastchat/train/train.py#L112
        model_inputs = {"input_ids": [], "labels": []}
        # max_length = data_args.max_source_length + data_args.max_target_length
        max_length = 2048
        for example in examples["conversations"]:
            input_ids, labels = [], []

            for turn in example:
                if turn["from"] == "seeker":
                    value_ids = tokenizer.encode(text=format_input(turn['value']), add_special_tokens=False)
                    input_ids += value_ids
                    labels += value_ids
                else:
                    value_ids = tokenizer.encode(text=turn['value'], add_special_tokens=False)
                    input_ids += value_ids + [tokenizer.eos_token_id]
                    labels += value_ids + [tokenizer.eos_token_id]

            # supporter_system = example['system']['supporter']
            # dials = example['history']
            # info = example['info']
            # utterance = example['utterance']

            # system = format_system(supporter_system)
            # value_ids = tokenizer.encode(text=system, add_special_tokens=False)
            # input_ids += value_ids
            # labels += [IGNORE_INDEX] * len(value_ids)

            # for turn in dials:
            #     if turn['from'] == 'seeker':
            #         cur_input = format_seeker(turn['value'])
            #     else:
            #         cur_input = format_supporter(turn['value'])
            #     value_ids = tokenizer.encode(text=cur_input, add_special_tokens=False)
            #     input_ids += value_ids
            #     labels += [IGNORE_INDEX] * len(value_ids)
            
            # info = format_info('SUPPORTER', info)
            # value_ids = tokenizer.encode(text=info, add_special_tokens=False)
            # input_ids += value_ids
            # labels += [IGNORE_INDEX] * len(value_ids)

            # value_ids = tokenizer.encode(text=utterance, add_special_tokens=False)
            # input_ids += value_ids + [tokenizer.eos_token_id]
            # labels += value_ids + [tokenizer.eos_token_id]

            if len(input_ids) > max_length:
                input_ids = input_ids[:max_length]
                labels = labels[:max_length]

            model_inputs["input_ids"].append(input_ids)
            model_inputs["labels"].append(labels)

        return model_inputs

    def preprocess_unsupervised_dataset(examples):
        # build inputs with format `<bos> X` and labels with format `<bos> Y`
        model_inputs = {"input_ids": [], "labels": []}

        for dialog in get_dialog(examples):
            prompt, answer = "".join(dialog[:-1]), dialog[-1]

            source_ids = tokenizer.encode(text=prompt, add_special_tokens=True)
            target_ids = tokenizer.encode(text=answer, add_special_tokens=True)

            if len(source_ids) > data_args.max_source_length:
                source_ids = source_ids[:data_args.max_source_length]
            if len(target_ids) > data_args.max_target_length:
                target_ids = target_ids[:data_args.max_target_length]

            model_inputs["input_ids"].append(source_ids)
            model_inputs["labels"].append(target_ids)

        return model_inputs

    def preprocess_pairwise_dataset(examples):
        # build input pairs with format `<bos> X Y1 <eos>` and `<bos> X Y2 <eos>`
        model_inputs = {"accept_ids": [], "reject_ids": []}
        for dialog in get_dialog(examples):
            prompt, answer = "".join(dialog[:-1]), dialog[-1]

            source_ids = tokenizer.encode(text=prompt, add_special_tokens=True)
            accept_ids = tokenizer.encode(text=answer[0], add_special_tokens=False)
            reject_ids = tokenizer.encode(text=answer[1], add_special_tokens=False)

            if len(source_ids) > data_args.max_source_length:
                source_ids = source_ids[:data_args.max_source_length]
            if len(accept_ids) > data_args.max_target_length - 1: # eos token
                accept_ids = accept_ids[:data_args.max_target_length - 1]
            if len(reject_ids) > data_args.max_target_length - 1: # eos token
                reject_ids = reject_ids[:data_args.max_target_length - 1]

            accept_ids = source_ids + accept_ids + [tokenizer.eos_token_id]
            reject_ids = source_ids + reject_ids + [tokenizer.eos_token_id]

            model_inputs["accept_ids"].append(accept_ids)
            model_inputs["reject_ids"].append(reject_ids)
        return model_inputs

    def print_supervised_dataset_example(example):
        print("input_ids:\n{}".format(example["input_ids"]))
        print("inputs:\n{}".format(tokenizer.decode(example["input_ids"], skip_special_tokens=False)))
        print("label_ids:\n{}".format(example["labels"]))
        print("labels:\n{}".format(
            tokenizer.decode([d if d != IGNORE_INDEX else tokenizer.pad_token_id for d in example["labels"]],
                             skip_special_tokens=False)
        ))

    def print_pairwise_dataset_example(example):
        print("accept_ids:\n{}".format(example["accept_ids"]))
        print("accepts:\n{}".format(tokenizer.decode(example["accept_ids"], skip_special_tokens=False)))
        print("reject_ids:\n{}".format(example["reject_ids"]))
        print("rejects:\n{}".format(tokenizer.decode(example["reject_ids"], skip_special_tokens=False)))

    def print_unsupervised_dataset_example(example):
        print("input_ids:\n{}".format(example["input_ids"]))
        print("inputs:\n{}".format(tokenizer.decode(example["input_ids"], skip_special_tokens=False)))

    if stage == "pt":
        preprocess_function = preprocess_pretrain_dataset
    elif stage == "sft":
        if not training_args.predict_with_generate:
            # preprocess_function = preprocess_supervised_dataset
            if data_args.model_type == 'base':
                preprocess_function = preprocess_model_base_dataset
            elif data_args.model_type == 'supporter':
                preprocess_function = preprocess_model_supporter_dataset
            elif data_args.model_type == 'seeker':
                preprocess_function = preprocess_model_seeker_dataset
        else:
            preprocess_function = preprocess_unsupervised_dataset
    elif stage == "rm":
        preprocess_function = preprocess_pairwise_dataset
    elif stage == "ppo":
        preprocess_function = preprocess_unsupervised_dataset

    with training_args.main_process_first(desc="dataset map pre-processing"):
        dataset = dataset.map(
            preprocess_function,
            batched=True,
            num_proc=data_args.preprocessing_num_workers,
            remove_columns=column_names,
            load_from_cache_file=not data_args.overwrite_cache,
            desc="Running tokenizer on dataset"
        )

        if stage == "pt":
            print_unsupervised_dataset_example(dataset[0])
        elif stage == "sft":
            print_supervised_dataset_example(dataset[0])
        elif stage == "rm":
            print_pairwise_dataset_example(dataset[0])
        elif stage == "ppo":
            print_unsupervised_dataset_example(dataset[0])

        return dataset
