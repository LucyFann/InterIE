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
from sig_parser.IEGraph import Graph

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

                elif line.startswith('{"doc_id":'):
                    mysig = SIGGraph(line)
                    yield tokens, lemmas, pos_tags, ner_tags, mysig
                '''                
                elif line.startswith('# ::entity_type '):
                    line = line.replace("\'", '\"')
                    entity_type = json.loads(line[len('# ::entity_type '):])
                elif line.startswith('# ::trigger '):
                    trigger_type = json.loads(json.dumps(eval(line[len('# ::trigger '):])))
                    # trigger_type = json.loads(line[len('# ::trigger '):])
                

                elif line.startswith('# ::save-date'):
                    graph_line = SIG.get_sig_line(f)
                    sig = SIG.parse_SIG_line(graph_line, do_reverse=do_reverse)
                    mysig = SIGGraph(sig)
                    
                    
                elif line.startswith('# ::mention_type '):
                    line = line.replace("\'", '\"')
                    mention_type = json.loads(line[len('# ::mention_type '):])
                elif line.startswith('# ::entity_subtype '):
                    line = line.replace("\'", '\"')
                    entity_subtype = json.loads(line[len('# ::entity_subtype '):])
                '''


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
    token, lemma, pos ,ner, sigs, entity_type, mention_type, entity_subtype, trigger_type = [], [], [], [], [], [], [], [], []
    for _tok, _lem, _pos, _ner, _mysig in SIGIO.read(filename, do_reverse=do_reverse):
        token.append(_tok)
        lemma.append(_lem)
        pos.append(_pos)
        ner.append(_ner)
        sigs.append(_mysig)
        '''
        entity_type.append(_entity_type)
        
        mention_type.append(_mention_type)
        entity_subtype.append(_entity_subtype)
        
        trigger_type.append(_trigger_type)
        '''
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
    args = parse_config()

    print(f'levi_graph = {args.levi_graph}')
    do_reverse = args.levi_graph != 'kahn'
    print(f'do_reverse = {do_reverse}')

    sigs, token, lemma, pos, ner = read_file(args.train_data, do_reverse=do_reverse)
    lexical_map = LexicalMap()

    # collect concepts and relations
    conc = []
    rel = []
    predictable_conc = []
    for i in range(10):
        # run 10 times random sort to get the priorities of different types of edges
        for sig, lem, tok in zip(sigs, lemma, token):

            concept, edge, not_ok = sig.root_centered_sort()
            if args.levi_graph is True:
                concept, edge = levi_sig([concept], [edge])
                concept, edge = concept[0], edge[0]
            elif args.levi_graph == 'kahn':
                concept, edge = sig.to_levi()
            lexical_concepts = set()
            cp_seq, mp_seq = lexical_map.get_concepts(lem, tok)
            for lc, lm in zip(cp_seq, mp_seq):
                lexical_concepts.add(lc)
                lexical_concepts.add(lm)
            if i == 0:
                predictable_conc.append([c for c in concept if c not in lexical_concepts])
                conc.append(concept)
            rel.append([e[-1] for e in edge])
    
    # make vocabularies
    token_vocab, token_char_vocab = make_vocab(token, char_level=True)
    lemma_vocab, lemma_char_vocab = make_vocab(lemma, char_level=True)
    pos_vocab = make_vocab(pos)
    ner_vocab = make_vocab(ner)
    #entity_type_vocab = make_vocab(entity_type)
    # mention_type_vocab = make_vocab(mention_type)
    # entity_subtype_vocab = make_vocab(entity_subtype)
    #trigger_type_vocab = make_vocab(trigger_type)
    conc_vocab, conc_char_vocab = make_vocab(conc, char_level=True)

    predictable_conc_vocab = make_vocab(predictable_conc)
    num_predictable_conc = sum(len(x) for x in predictable_conc)
    num_conc = sum(len(x) for x in conc)
    print('predictable concept coverage', num_predictable_conc, num_conc, num_predictable_conc / num_conc)
    rel_vocab = make_vocab(rel)

    print('make vocabularies')
    write_vocab(token_vocab, 'tok_vocab')
    write_vocab(token_char_vocab, 'word_char_vocab')
    write_vocab(lemma_vocab, 'lem_vocab')
    write_vocab(lemma_char_vocab, 'lem_char_vocab')
    write_vocab(pos_vocab, 'pos_vocab')
    write_vocab(ner_vocab, 'ner_vocab')
    write_vocab(conc_vocab, 'concept_vocab')
    write_vocab(conc_char_vocab, 'concept_char_vocab')
    write_vocab(predictable_conc_vocab, 'predictable_concept_vocab')
    write_vocab(rel_vocab, 'rel_vocab')
    #write_vocab(entity_type_vocab, 'entity_type_vocab')

    # write_vocab(mention_type_vocab, 'mention_type_vocab')
    # write_vocab(entity_subtype_vocab, 'entity_subtype_vocab')
    #write_vocab(trigger_type_vocab, 'trigger_type_vocab')


