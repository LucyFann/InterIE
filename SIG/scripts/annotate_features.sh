#!/usr/bin/env bash

set -e

# Start a Stanford CoreNLP server before running this script.
# https://stanfordnlp.github.io/CoreNLP/corenlp-server.html

# The compound file is downloaded from
# https://github.com/ChunchuanLv/SIG_AS_GRAPH_PREDICTION/blob/master/data/joints.txt
compound_file=data/SIG/joints.txt
sig_dir=$1

python3 -u -m stog.data.dataset_readers.sig_parsing.preprocess.feature_annotator \
    ${sig_dir}/test.txt ${sig_dir}/train.txt ${sig_dir}/dev.txt \
    --compound_file ${compound_file}
