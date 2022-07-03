import json

import penman

from stog.data.dataset_readers.sig_parsing.sig import SIG, SIGGraph


class SIGIO:

    def __init__(self):
        pass

    @staticmethod
    def read(file_path):
        with open(file_path, encoding='utf-8') as f:
            sig = SIG()
            graph_lines = []
            misc_lines = []
            for line in f:
                line = line.rstrip()
                if line == '':
                    if len(graph_lines) != 0:
                        while True:
                            try:
                                sig.graph = SIGGraph.decode(' '.join(graph_lines))
                                break
                            except penman.DecodeError:
                                _graph_lines = [x for x in graph_lines if ' / ' in x]
                                if not graph_lines or len(graph_lines) == len(_graph_lines):
                                    graph_lines = ['(c0 / multi-sentence)']
                                else:
                                    graph_lines = _graph_lines
                        sig.graph.set_src_tokens(sig.get_src_tokens())
                        sig.misc = misc_lines
                        yield sig
                        sig = SIG()
                    graph_lines = []
                    misc_lines = []
                elif line.startswith('# ::'):
                    if line.startswith('# ::id '):
                        sig.id = line[len('# ::id '):]
                    elif line.startswith('# ::snt '):
                        sig.sentence = line[len('# ::snt '):]
                    elif line.startswith('# ::tokens '):
                        sig.tokens = json.loads(line[len('# ::tokens '):])
                    elif line.startswith('# ::lemmas '):
                        sig.lemmas = json.loads(line[len('# ::lemmas '):])
                    elif line.startswith('# ::pos_tags '):
                        sig.pos_tags = json.loads(line[len('# ::pos_tags '):])
                    elif line.startswith('# ::ner_tags '):
                        sig.ner_tags = json.loads(line[len('# ::ner_tags '):])
                    elif line.startswith('# ::abstract_map '):
                        sig.abstract_map = json.loads(line[len('# ::abstract_map '):])
                    else:
                        misc_lines.append(line)
                else:
                    graph_lines.append(line)

            if len(graph_lines) != 0:
                sig.graph = SIGGraph.decode(' '.join(graph_lines))
                sig.graph.set_src_tokens(sig.get_src_tokens())
                sig.misc = misc_lines
                yield sig

    @staticmethod
    def dump(sig_instances, f):
        for sig in sig_instances:
            f.write(str(sig) + '\n\n')
