import os
import re
import json
from copy import copy

import penman

from stog.data.dataset_readers.sig_parsing.io import SIGIO
from stog.data.dataset_readers.sig_parsing.sig_concepts import Polarity, Polite

from stog.utils import logging

logger = logging.init_logger()

TRIVIAL_TOKENS = ('and', 'in', 'on', 'of', 'de', 'da')


def normalize_text(text):
    text = text.replace(' - ', '-').replace(" 's", "'s").replace(' , ', ', ')
    tokens = text.split()
    if any(t[0].isupper() for t in tokens):
        n_tokens = []
        for token in tokens:
            if token not in TRIVIAL_TOKENS and not any(c.isupper() for c in token):
                token = token[0].upper() + token[1:]
            n_tokens.append(token)
        text = ' '.join(n_tokens)
    if len(tokens) == 1 and tokens[0][0].islower():
        text = text.capitalize()
    if len(tokens) == 1 and tokens[0].isupper() and tokens[0].isalpha() and len(tokens[0]) > 6:
        text = token[0].upper() + token[1:].lower()
    return text


class Expander:

    def __init__(self, util_dir):
        self.util_dir = util_dir
        self.name_ops_map = {}
        self.nationality_map = {}
        self._load_utils()
        self.name_node_expand_count = 0
        self.date_node_expand_count = 0
        self.score_node_expand_count = 0
        self.url_expand_count = 0
        self.ordinal_node_expand_count = 0
        self.quantity_expand_count = 0
        self.correctly_restored_count = 0

    def reset_stats(self):
        self.name_node_expand_count = 0
        self.date_node_expand_count = 0
        self.score_node_expand_count = 0
        self.quantity_expand_count = 0
        self.url_expand_count = 0
        self.ordinal_node_expand_count = 0

    def print_stats(self):
        logger.info('Restored {} name nodes.'.format(self.correctly_restored_count))
        logger.info('Expanded {} name nodes.'.format(self.name_node_expand_count))
        logger.info('Expanded {} date nodes.'.format(self.date_node_expand_count))
        logger.info('Expanded {} score nodes.'.format(self.score_node_expand_count))
        logger.info('Expanded {} ordinal nodes.'.format(self.ordinal_node_expand_count))
        logger.info('Expanded {} quantities.'.format(self.quantity_expand_count))
        logger.info('Expanded {} urls.'.format(self.url_expand_count))

    def expand_file(self, file_path):
        for i, sig in enumerate(SIGIO.read(file_path)):
            self.expand_graph(sig)
            yield sig
        self.print_stats()

    def expand_graph(self, sig):
        graph = sig.graph
        _graph = copy(graph)
        self.restore_polarity(sig)
        try:
            str(sig)
        except penman.EncodeError:  # i == 237 triggers a bug in restore_polarity
            sig.graph = _graph
        abstract_map = sig.abstract_map
        nodes = list(graph.get_nodes())
        for abstract, saved_dict in abstract_map.items():
            abstract_type = saved_dict['type']
            for node in nodes:
                if node.instance == abstract:
                    if abstract_type == 'named-entity':
                        self.expand_name_node(node, saved_dict, sig)
                        self.name_node_expand_count += 1

                    if abstract_type == 'date-entity':
                        self.expand_date_node(node, saved_dict, sig)
                        self.date_node_expand_count += 1

                    if abstract_type == 'score-entity':
                        self.expand_score_node(node, saved_dict, sig)
                        self.score_node_expand_count += 1

                    if abstract_type == 'ordinal-entity':
                        self.expand_ordinal_node(node, saved_dict, sig)
                        self.ordinal_node_expand_count += 1

                for attr, value in node.attributes[:]:
                    if str(value) == abstract:
                        if abstract_type == 'quantity':
                            if isinstance(saved_dict['value'], str) and "/" in saved_dict['value']:
                                saved_dict['value'] = '"' + saved_dict['value'] + '"'
                            graph.replace_node_attribute(node, attr, value, saved_dict['value'])
                            self.quantity_expand_count += 1

                        if abstract_type == 'url-entity':
                            graph.replace_node_attribute(node, attr, value, saved_dict['value'])
                            self.url_expand_count += 1

    def restore_polarity(self, sig):
        polarity = Polarity(sig)
        polarity.predict_polarity()
        polarity.restore_polarity()
        polite = Polite(sig)
        polite.predict_polite()
        polite.restore_polite()

    def get_ops(self, saved_dict):
        span = saved_dict['span']
        if span.lower() in self.nationality_map:
            span = self.nationality_map[span.lower()]
        if span.lower() in self.name_ops_map:
            span = max(self.name_ops_map[span.lower()].items(), key=lambda x: x[1])[0]
        else:
            span = normalize_text(span)
            if span.lower() in self.nationality_map:
                span = self.nationality_map[span.lower()]
        ops = []
        for op in span.split():
            if re.search(r'^\d*\.*\d*$', op):
                if '.' in op:
                    op = float(op)
                else:
                    op = int(op)
            else:
                op = '"{}"'.format(op)
            ops.append(op)
        if span == saved_dict['ops']:
            self.correctly_restored_count += 1
        return ops

    def expand_name_node(self, node, saved_dict, sig):
        graph = sig.graph
        ops = self.get_ops(saved_dict)
        old = node.instance
        graph.replace_node_attribute(node, 'instance', old, 'name')
        for i, op in enumerate(ops, 1):
            graph.add_node_attribute(node, 'op{}'.format(i), op)

    def expand_date_node(self, node, saved_dict, sig):
        graph = sig.graph
        attrs = saved_dict['attrs']
        graph.replace_node_attribute(node, 'instance', node.instance, 'date-entity')
        for key, value in attrs.items():
            graph.add_node_attribute(node, key, value)
        edges = saved_dict['edges']
        for label, instance in edges.items():
            target = graph.add_node(instance)
            graph.add_edge(node, target, label)

    def expand_score_node(self, node, saved_dict, sig):
        graph = sig.graph
        graph.replace_node_attribute(node, 'instance', node.instance, 'score-entity')
        for i, op in enumerate(saved_dict['ops'], 1):
            graph.add_node_attribute(node, 'op{}'.format(i), op)

    def expand_ordinal_node(self, node, saved_dict, sig):
        graph = sig.graph
        graph.replace_node_attribute(node, 'instance', node.instance, 'ordinal-entity')
        graph.add_node_attribute(node, 'value', int(saved_dict['ops'][0]))

    def _load_utils(self):
        with open(os.path.join(self.util_dir, 'name_op_cooccur_counter.json'), encoding='utf-8') as f:
            self.name_ops_map = json.load(f)
            self.name_ops_map['u.n.'].pop('United Nations')

        # The country list is downloaded from github:
        # https://github.com/Dinu/country-nationality-list
        with open(os.path.join(self.util_dir, 'countries.json'), encoding='utf-8') as f:
            countries = json.load(f)
            for country in countries:
                nationalities = [n.strip() for n in country['nationality'].split(',')]
                if len(nationalities) > 1 and 'Chinese' in nationalities:
                    nationalities.remove('Chinese')
                for nationality in nationalities:
                    self.nationality_map[nationality.lower()] = country['en_short_name']
        self.nationality_map['american'] = 'United States'
        self.nationality_map['british'] = 'Britain'
        self.nationality_map['brazilians'] = 'Brazil'
        self.nationality_map['russian'] = 'Russia'
        self.nationality_map['north korean'] = 'North Korea'
        self.nationality_map['south korean'] = 'South Korea'
        self.nationality_map['himalayan'] = 'Himalaya'
        self.nationality_map['venezuelan'] = 'Venezuela'
        self.nationality_map['kirghizian'] = 'Kirghizia'
        self.nationality_map['venezuelans'] = 'Venezuela'
        self.nationality_map['shiites'] = 'Shiite'


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('expander.py')
    parser.add_argument('--sig_files', nargs='+', default=[])
    parser.add_argument('--util_dir', required=True)

    args = parser.parse_args()

    expander = Expander(util_dir=args.util_dir)

    for file_path in args.sig_files:
        with open(file_path + '.expand', 'w', encoding='utf-8') as f:
            for sig in expander.expand_file(file_path):
                f.write(str(sig) + '\n\n')
