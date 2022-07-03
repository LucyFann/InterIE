import os
import re
import json
from typing import List, Dict, Set
from collections import defaultdict

from stog.data.dataset_readers.sig_parsing.io import SIGIO
from stog.data.dataset_readers.sig_parsing.sig import SIG


def prev_token_is(index: int, k: int, sig: SIG, pattern: str):
    if index - k >= 0:
        return re.match(pattern, sig.lemmas[index - k])


def next_token_is(index: int, k: int, sig: SIG, pattern: str):
    if index + k < len(sig.lemmas):
        return re.match(pattern, sig.lemmas[index + k])


def is_anonym_type(index: int, sig: SIG, text_map: Dict, types: List) -> bool:
    lemma = sig.lemmas[index]
    return lemma in text_map and text_map[lemma]['ner'] in types


class TextAnonymizor:

    def __init__(self,
                 text_maps: Dict,
                 priority_lists: List,
                 _VNE: str,
                 _LOCEN1: List,
                 _LOCEN2: List,
                 _N: List,
                 _M: List,
                 _R: List,
                 _INVP: List,
                 _INVS: List,
                 ) -> None:
        self._text_maps = text_maps
        self._priority_lists = priority_lists
        self._VNE = _VNE
        self._LOCEN1 = _LOCEN1
        self._LOCEN2 = _LOCEN2
        self._N = _N
        self._M = _M
        self._R = _R
        self._INVP = _INVP
        self._INVS = _INVS

    def __call__(self, sig: SIG) -> Dict:
        anonymization_map = {}
        for anonym_type, (text_map, pos_tag) in self._text_maps.items():
            max_length = len(max(text_map, key=len))
            anonymization_map.update(self._abstract(
                sig, text_map, max_length, anonym_type, pos_tag
            ))
        return anonymization_map

    def _abstract(self,
                  sig: SIG,
                  text_map: Dict,
                  max_length: int,
                  anonym_type: str,
                  pos_tag: str) -> Dict:
        replaced_spans = {}
        collected_entities = set()
        ignored_spans = self._get_ignored_spans(sig)
        while True:
            done = self._replace_span(
                sig,
                text_map,
                max_length,
                anonym_type,
                pos_tag,
                ignored_spans,
                replaced_spans,
                collected_entities,
            )
            if done:
                break
        ner_counter = defaultdict(int)
        anonymization_map = {}
        for i, lemma in enumerate(sig.lemmas):
            if lemma in replaced_spans:
                if anonym_type == 'quantity':
                    ner = lemma.rsplit('_', 2)[1]
                else:
                    ner = lemma.rsplit('_', 1)[0]
                ner_counter[ner] += 1

                if anonym_type == 'quantity':
                    if ner in ('1', '10', '100', '1000') or not re.search(r"[\./]", ner):
                        anonym_lemma = str(int(ner) * ner_counter[ner])
                    else:
                        anonym_lemma = str(float(ner) * ner_counter[ner])
                else:
                    anonym_lemma = ner + '_' + str(ner_counter[ner])

                sig.lemmas[i] = anonym_lemma
                sig.tokens[i] = anonym_lemma
                anonymization_map[anonym_lemma] = replaced_spans[lemma]
        return anonymization_map

    def _leave_as_is(self,
                     index: int,
                     sig: SIG,
                     text_map: Dict,
                     anonym_type: str) -> bool:
        if anonym_type == 'named-entity':
            if sig.pos_tags[index].startswith('V') and not next_token_is(index, 1, sig, self._VNE):
                return True
            if (is_anonym_type(index, sig, text_map, ["LOCATION", "ENTITY"])
                    and next_token_is(index, 0, sig, self._LOCEN1[0]) and (
                        prev_token_is(index, 1, sig, self._LOCEN1[1]) or
                        next_token_is(index, 1, sig, self._LOCEN1[2]))):
                return True
            if next_token_is(index, 0, sig, self._LOCEN2[0]) and prev_token_is(index, 1, sig, self._LOCEN2[1]):
                return True

        if anonym_type == 'ordinal-entity':
            if next_token_is(index, 0, sig, r"^\d+th$") and not prev_token_is(index, 1, sig, self._M):
                return False
            if len(sig.lemmas[index]) == 1 and sig.lemmas[index].isdigit() and (
                    next_token_is(index, 1, sig, self._R[0]) or next_token_is(index, 2, sig, self._R[1])):
                return False
            if index == len(sig.lemmas) - 2 and sig.pos_tags[index + 1] in '.,!?':
                return True
            if prev_token_is(index, 1, sig, self._INVP[0]) or next_token_is(index, 1, sig, self._INVS[0]):
                return True
            if  not prev_token_is(index, 2, sig, self._INVP[1]) and next_token_is(index, 1, sig, self._INVS[1]):
                return True
            if next_token_is(index, 1, sig, self._R[1]) and (
                    not next_token_is(index, 3, sig, self._VNE) or prev_token_is(index, 1, sig, r"^ORDINAL")):
                return True

        if anonym_type == 'date-entity':
            if is_anonym_type(index, sig, text_map, ['DATE_ATTRS']) and next_token_is(index, 1, sig, r"^''$"):
                    return True
            if (sig.lemmas[index].isdigit() and len(sig.lemmas[index]) < 4 and (
                        prev_token_is(index, 1, sig, self._INVP[2]) or next_token_is(index, 1, sig, self._INVS[2]))):
                return True
            if sig.lemmas[index].isalpha() and (prev_token_is(index, 1, sig, self._INVP[3]) or next_token_is(index, 1, sig, self._INVS[3])):
                return True

        if anonym_type == 'quantity':
            if len(sig.lemmas[index]) == 1 and prev_token_is(index, 2, sig, self._INVP[4]) and next_token_is(index, 1, sig, self._INVP[4]):
                return True
            if ' '.join(sig.lemmas[index - 2: index + 2]) in self._N[2:4]:
                return True
        else:
            if index == 0 and len(sig.lemmas[index]) == 1 and sig.lemmas[index].isdigit():
                return True

        if anonym_type != 'ordinal-entity':
            if sig.ner_tags[index] == 'ORDINAL' and not next_token_is(index, 0, sig, self._N[1]):
                return True

        if next_token_is(index, 0, sig, self._N[0]) and (
                prev_token_is(index, 1, sig, self._INVP[5]) or next_token_is(index, 1, sig, self._INVS[5])):
            return True

        return False

    def _replace_span(self,
                      sig: SIG,
                      text_map: Dict,
                      max_length: int,
                      anonym_type: str,
                      pos_tag: str,
                      ignored_spans: Set,
                      replaced_spans: Dict,
                      collected_entities: Set) -> bool:
        for length in range(max_length, 0, -1):
            for start in range(len(sig.lemmas) + 1 - length):
                if length == 1 and self._leave_as_is(start, sig, text_map, anonym_type):
                    continue
                span1 = ' '.join(sig.tokens[start:start + length])
                span2 = ' '.join(sig.lemmas[start:start + length])
                if span1 in ignored_spans or span2 in ignored_spans:
                    continue
                if span1 in text_map or span2 in text_map:
                    value = text_map.get(span1, None) or text_map.get(span2, None)
                    if anonym_type == 'named-entity':
                        entity_name = value['lemma'] if 'lemma' in value else value['ops']
                        if entity_name in collected_entities:
                            continue
                        else:
                            collected_entities.add(entity_name)
                    anonym_lemma = value['ner'] + '_' + str(len(replaced_spans))
                    pos_tag = sig.pos_tags[start] if anonym_type == 'quantity' else pos_tag
                    ner = 'NUMBER' if anonym_type == 'quantity' else value['ner']
                    replaced_spans[anonym_lemma] = value
                    sig.replace_span(list(range(start, start + length)), [anonym_lemma], [pos_tag], [ner])
                    return False
        return True

    def _get_ignored_spans(self, sig: SIG) -> Set:
        ignored_spans = set()
        for spans in self._priority_lists:
            for i, span in enumerate(spans):
                tokens = span.split()
                if len(tokens) > 1:
                    if span + ' ' in ' '.join(sig.lemmas) or span + ' ' in ' '.join(sig.tokens):
                        ignored_spans.update(spans[i + 1:])
                        break
                else:
                    if span in sig.lemmas or span in sig.tokens:
                        ignored_spans.update(spans[i + 1:])
                        break
        return ignored_spans

    @classmethod
    def from_json(cls, file_path: str) -> 'TextAnonymizor':
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
        return cls(
            text_maps=d["text_maps"],
            priority_lists=d["priority_lists"],
            _VNE=d["VNE"],
            _LOCEN1=d["LOCEN1"],
            _LOCEN2=d["LOCEN2"],
            _N=d["N"],
            _M=d["M"],
            _R=d["R"],
            _INVP=d["INVP"],
            _INVS=d["INVS"],
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("text_anonymizor.py")

    parser.add_argument('--sig_file', required=True, help="File to anonymize.")
    parser.add_argument('--util_dir')
    args = parser.parse_args()

    text_anonymizor = TextAnonymizor.from_json(
        os.path.join(args.util_dir, "text_anonymization_rules.json"))

    with open(args.sig_file + ".recategorize", "w", encoding="utf-8") as f:
        for sig in SIGIO.read(args.sig_file):
            sig.abstract_map = text_anonymizor(sig)
            f.write(str(sig) + "\n\n")
