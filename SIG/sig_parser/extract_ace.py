#!/usr/bin/env python
# coding: utf-8

from collections import Counter
import json

import sys
sys.path.append(".")
from sig_parser.sig import SIG
from sig_parser.SIGGraph import SIGGraph
from sig_parser.SIGGraph import _is_abs_form
from elit.datasets.parsing.sig import levi_sig


class SIGIO:

    def __init__(self):
        pass

    @staticmethod
    def read(file_path, do_reverse=True):
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('# ::id '):
                    sig_id = line[len('# ::id '):]
                elif line.startswith('# ::snt '):
                    sentence = line[len('# ::snt '):]
                elif line.startswith('# ::tokens '):
                    tokens = json.loads(line[len('# ::tokens '):])
                elif line.startswith('# ::lemmas '):
                    lemmas = json.loads(line[len('# ::lemmas '):])
                    lemmas = [le if _is_abs_form(le) else le.lower() for le in lemmas]
                elif line.startswith('# ::pos_tags '):
                    pos_tags = json.loads(line[len('# ::pos_tags '):])
                elif line.startswith('# ::ner_tags '):
                    ner_tags = json.loads(line[len('# ::ner_tags '):])
                elif line.startswith('# ::save-date'):
                    graph_line = SIG.get_sig_line(f)
                    sig = SIG.parse_SIG_line(graph_line, do_reverse=do_reverse)
                    mysig = SIGGraph(sig)
                    yield tokens, lemmas, pos_tags, ner_tags, mysig


class LexicalMap(object):

    # build our lexical mapping (from token/lemma to concept), useful for copy mechanism.
    def __init__(self):
        pass

    # cp_seq, mp_seq, token2idx, idx2token = lex_map.get(lemma, token, vocabs['predictable_concept'])
    def get_concepts(self, lem, tok, vocab=None, rel_vocab=None):
        cp_seq, mp_seq = [], []
        new_tokens = set()
        for le, to in zip(lem, tok):
            cp_seq.append(le + '_')
            mp_seq.append(le)

        if vocab is None:
            return cp_seq, mp_seq

        for cp, mp in zip(cp_seq, mp_seq):
            if vocab.token2idx(cp) == vocab.unk_idx:
                new_tokens.add(cp)
            if vocab.token2idx(mp) == vocab.unk_idx:
                new_tokens.add(mp)
        nxt = vocab.size
        token2idx, idx2token = dict(), dict()
        if rel_vocab:
            new_tokens = rel_vocab._idx2token + sorted(new_tokens)
        else:
            new_tokens = sorted(new_tokens)
        for x in new_tokens:
            token2idx[x] = nxt
            idx2token[nxt] = x
            nxt += 1
        return cp_seq, mp_seq, token2idx, idx2token


def read_file(filename, do_reverse=True):
    # read preprocessed sig file
    token, lemma, pos, ner, sigs = [], [], [], [], []
    for _tok, _lem, _pos, _ner, _mysig in SIGIO.read(filename, do_reverse=do_reverse):
        token.append(_tok)
        lemma.append(_lem)
        pos.append(_pos)
        ner.append(_ner)
        sigs.append(_mysig)


    print('read from %s, %d sigs' % (filename, len(token)))
    return sigs, token, lemma, pos, ner


def make_vocab(batch_seq, char_level=False):
    cnt = Counter()
    for seq in batch_seq:
        cnt.update(seq)
    if not char_level:
        return cnt
    char_cnt = Counter()
    for x, y in cnt.most_common():
        for ch in list(x):
            char_cnt[ch] += y
    return cnt, char_cnt


def write_vocab(vocab, path):
    with open(path, 'w') as fo:
        for x, y in vocab.most_common():
            fo.write('%s\t%d\n' % (x, y))


import argparse


def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str)

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        elif v == 'kahn':
            return v
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser.add_argument("--levi_graph", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Use Levi graph.")
    return parser.parse_args()


if __name__ == "__main__":

    sig = './data/SIG/ace_sig//train.txt.features.preproc'
    ace = './data/ace_oneie/train.oneie.json'
    res = read_file(sig)


    # entity_vocab = make_vocab(entity)


    print('make vocabularies')

    # write_vocab(ner_vocab, 'ner_vocab')



