# InterIE

### environment

- `conda create -n your_envname python=3.7`
- `conda activate your_envname`
- `sh set_environments.sh`

## SIG Generation

### Data Preparation

0. You need to transform AMRIE datafile(use script in [OneIE](https://aclanthology.org/2020.acl-main.713/)) `train.oneie.json`,`dev.oneie.json`,`test.oneie.json`  into SIG format , the SIG G(V, E) is a rooted, directed and labeled graph. The node of SIG represents an entity or an event trigger. The edge of SIG denotes label (i.e., entity type, relation type and argument). and put it into `data/ACE`

1. Feature Annotation: we use stanfordCoreNLP (version **3.9.2**) for lemmatizing, POS tagging, etc.

   `sh run_standford_corenlp_server.sh`

   `sh scripts/annotate_features.sh data/ACE`

2. Building Vocabs

   `sh scripts/prepare_vocab.sh data/ACE/ true`

### Training

`sh scripts/train_joint.sh data/ACE`

## Graph Aggregate

Todo

### Training

### Testing

## Acknowledgement

This code is largely based on [AMRIE](https://github.com/zhangzx-uiuc/AMR-IE) and [AMR-gs](https://github.com/jcyk/AMR-gs) . Many thanks to [zhang et al.](https://www.aclweb.org/anthology/2021.naacl-main.4/) and [Cai et al.](https://arxiv.org/abs/2004.05572) for publicizing their codes.

