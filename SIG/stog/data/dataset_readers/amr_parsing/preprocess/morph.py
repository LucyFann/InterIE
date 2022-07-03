from collections import defaultdict

from stog.data.dataset_readers.sig_parsing.io import SIGIO
from stog.utils import logging


logger = logging.init_logger()


class Morph:

    def __init__(self, file_path):
        self.morph_dict = defaultdict(list)
        self._load(file_path)
        self.morph_count = 0

    def _load(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                parts = line.strip().split('::DERIV-')[1:]
                key = None
                for part in parts:
                    token_type, token = part.strip().split(' ', 1)
                    token = token[1:-1]
                    if token_type == 'VERB':
                        key = token
                    elif token_type == 'NOUN' and '-' not in token and token != key:
                        assert key is not None
                        self.morph_dict[token].append([key])
                    elif token_type == 'NOUN-ACTOR' and '-' not in token:
                        assert key is not None
                        self.morph_dict[token].append([key, 'person'])

    def read(self, file_path):
        for sig in SIGIO.read(file_path):
            yield self(sig)

    def __call__(self, sig):
        offset = 0
        for i in range(len(sig.tokens)):
            index = i + offset
            lemma = sig.lemmas[index]
            token = sig.tokens[index]
            morphed_lemmas = None
            if lemma in self.morph_dict:
                morphed_lemmas = self.morph_dict[lemma][0]
            elif token in self.morph_dict:
                morphed_lemmas = self.morph_dict[token][0]
            if morphed_lemmas is not None:
                pos = [sig.pos_tags[index]]
                ner = [sig.ner_tags[index]]
                if len(morphed_lemmas) == 2:
                    pos = ['VBG', 'NN']
                    ner.append('O')
                sig.replace_span([index], morphed_lemmas, pos, ner)
                offset += len(morphed_lemmas) - 1
                self.morph_count += 1
        return sig


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('morph.py')
    parser.add_argument('--sig_files', nargs='+', required=True)
    parser.add_argument('--morph_verbalization_file',
                        default='./data/misc/morph-verbalization-v1.01.txt')

    args = parser.parse_args()

    morph = Morph(args.morph_verbalization_file)

    for file_path in args.sig_files:
        with open(file_path + '.morph', 'w', encoding='utf-8') as f:
            for sig in morph.read(file_path):
                f.write(str(sig) + '\n\n')
            logger.info('Morphed {} tokens'.format(morph.morph_count))
            morph.morph_count = 0
