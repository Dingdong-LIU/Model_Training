export CUDA_VISIBLE_DEVICES=0
python run_summarization.py \
    --model_name_or_path model/for_claims/checkpoint/train-300-t1 \
    --do_train false \
    --do_eval true \
    --do_predict true \
    --train_file data/claims/train.csv \
    --validation_file data/claims/evaluation-auto-driving.csv \
    --test_file data/claims/evaluation-bitcoin-invest.csv \
    --text_column text \
    --summary_column claim \
    --source_prefix "claim: " \
    --output_dir model/for_claims/evaluation \
    --overwrite_output_dir \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate \
    --load_best_model_at_end false \
    --num_train_epochs 0 \
    --gradient_accumulation_steps 4 \
    --no_cuda false \
    --ignore_pad_token_for_loss true \
    --evaluation_strategy steps \
    --logging_steps 500
    # --evaluation_strategy epoch \
    