CUDA_VISIBLE_DEVICES=0 python model/LLaMA-Efficient-Tuning/src/train_bash.py \
    --stage sft \
    --model_type base \
    --model_name_or_path model/models/Llama-2-7b-hf \
    --do_train \
    --dataset model_base_dataset \
    --finetuning_type lora \
    --output_dir model/output/model_base \
    --overwrite_cache \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate 5e-5 \
    --num_train_epochs 2.0 \
    --plot_loss \
    --fp16 \
    --quantization_bit 4
