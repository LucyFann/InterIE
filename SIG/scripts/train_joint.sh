dataset=$1
ace=$2
python3 sig_parser/train.py --tok_vocab ${dataset}/tok_vocab\
                --ace_json ${ace} \
                --lem_vocab ${dataset}/lem_vocab\
                --pos_vocab  ${dataset}/pos_vocab\
                --ner_vocab ${dataset}/ner_vocab\
                --concept_vocab ${dataset}/concept_vocab\
                --predictable_concept_vocab ${dataset}/predictable_concept_vocab\
                --rel_vocab ${dataset}/rel_vocab\
                --word_char_vocab ${dataset}/word_char_vocab\
                --concept_char_vocab ${dataset}/concept_char_vocab\
                --train_data ${dataset}/train.txt.features.preproc \
                --entity_type_vocab ${dataset}/entity_type_vocab\
                --trigger_type_vocab ${dataset}/trigger_type_vocab\
                --dev_data ${dataset}/dev.txt.features.preproc  \
                --test_data ${dataset}/test.txt.features.preproc  \
                --with_bert \
                --joint_arc_concept \
                --bert_path bert-base-cased \
                --word_char_dim 32\
                --word_dim 300\
                --pos_dim 32\
                --ner_dim 16\
                --entity_type_dim 0\
                --trigger_type_dim 0\
                --concept_char_dim 32\
                --concept_dim 300 \
                --rel_dim 100 \
                --cnn_filter 3 256\
                --char2word_dim 128\
                --char2concept_dim 128\
                --embed_dim 512\
                --ff_embed_dim 1024\
                --num_heads 8\
                --snt_layers 4\
                --graph_layers 2\
                --inference_layers 4\
                --dropout 0.2\
                --unk_rate 0.33\
                --epochs 100000\
                --max_batches_acm 60000\
                --train_batch_size 4444\
                --dev_batch_size 4444 \
                --test_batch_size 4444 \
                --lr_scale 1. \
                --warmup_steps 2000\
                --print_every 100 \
                --eval_every 100 \
                --batches_per_update 4 \
                --ckpt model/ACE-R_4444 \
                --world_size 1\
                --gpus 1\
                --MASTER_ADDR localhost\
                --MASTER_PORT 29505\
                --start_rank 0
