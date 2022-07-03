# encoding=utf8
import os

import re
import random
import json
from collections import defaultdict
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from toposort import toposort, CircularDependencyError

from elit.components.sig.sig_parser.data import REL
import copy
number_regexp = re.compile(r'^-?(\d)+(\.\d+)?$')
abstract_regexp0 = re.compile(r'^([A-Z]+_)+\d+$')
abstract_regexp1 = re.compile(r'^\d0*$')
discard_regexp = re.compile(r'^n(\d+)?$')

attr_value_set = set(['-', '+', 'interrogative', 'imperative', 'expressive'])

def _is_attr_form(x):
    return (x in attr_value_set or x.endswith('_') or number_regexp.match(x) is not None)

def _is_abs_form(x):
    return (abstract_regexp0.match(x) is not None or abstract_regexp1.match(x) is not None)


def is_attr_or_abs_form(x):
    return _is_attr_form(x) or _is_abs_form(x)


def need_an_instance(x):
    return (not _is_attr_form(x) or (abstract_regexp0.match(x) is not None))


class SIGGraph(object):
    def __init__(self, smatch_sig):
        # transform sig from original smatch format into our own data structure

        self.IEinfo = json.loads(smatch_sig)
        # instance_triple, attribute_triple, relation_triple = smatch_sig.get_triples()
    
        instance_triple = [("instance","root","root")]
        relation_triple = []
        # attribute_triple = []        
        self.name2concept = dict()
        self.nodes = set()
        self.edges = dict()
        self.reversed_edges = dict()
        self.undirected_edges = dict()
        # entity
        for e in self.IEinfo['entity_mentions']:
            self._add_edge(e['entity_type'], "root", e['id'])
            instance_triple.append(("instance",e['id'],e['text']))

        for e in self.IEinfo['event_mentions']:
            instance_triple.append(("instance",e['id'],e['trigger']['text']))
            self._add_edge(e['event_type'], "root", e['id'])
            for arg in e['arguments']:
                relation_triple.append((arg['role'],arg['entity_id'],e['id']))
        # re
        for rel in self.IEinfo['relation_mentions']:   
            relation_triple.append((rel['relation_type'],rel['arguments'][0]['entity_id'],rel['arguments'][1]['entity_id']))
        # self.root = smatch_sig.root
        self.root = "root"
    
        # will do some adjustments
        self.abstract_concepts = dict()
        for _, name, concept in instance_triple:
            if is_attr_or_abs_form(concept):
                if _is_abs_form(concept):
                    self.abstract_concepts[name] = concept
                else:
                    pass
                    # print ('bad concept', _, name, concept)
            self.name2concept[name] = concept
            self.nodes.add(name)
        '''
        for rel, concept, value in attribute_triple:
            if rel == 'TOP':
                continue
            # discard some empty names
            if rel == 'name' and discard_regexp.match(value):
                continue
            # abstract concept can't have an attribute
            if concept in self.abstract_concepts:
                # print (rel, self.abstract_concepts[concept], value, "abstract concept cannot have an attribute")
                continue
            name = "%s_attr_%d" % (value, len(self.name2concept))
            if not _is_attr_form(value):
                if _is_abs_form(value):
                    self.abstract_concepts[name] = value
                else:
                    # print ('bad attribute', rel, concept, value)
                    continue
            self.name2concept[name] = value
            self._add_edge(rel, concept, name)
        '''
        for rel, head, tail in relation_triple:
            self._add_edge(rel, head, tail)

        # lower concept
        for name in self.name2concept:
            v = self.name2concept[name]
            if not _is_abs_form(v):
                v = v.lower()
            self.name2concept[name] = v

    def __len__(self):
        return len(self.name2concept)

    def _add_edge(self, rel, src, des):
        self.nodes.add(src)
        self.nodes.add(des)
        self.edges[src] = self.edges.get(src, []) + [(rel, des)]
        self.reversed_edges[des] = self.reversed_edges.get(des, []) + [(rel, src)]
        self.undirected_edges[src] = self.undirected_edges.get(src, []) + [(rel, des)]
        self.undirected_edges[des] = self.undirected_edges.get(des, []) + [(rel + '_reverse_', src)]

    def root_centered_sort(self, rel_order=None, shuffle=True):
        queue = [self.root]
   
        visited = set(queue)
        step = 0
        while len(queue) > step:
            src = queue[step]
            step += 1
            if src not in self.undirected_edges:
                continue
            if shuffle:
    
                random.shuffle(self.undirected_edges[src])
            if rel_order is not None:
                # Do some random thing here for performance enhancement
                if shuffle and random.random() < 0.5:
                    self.undirected_edges[src].sort(
                        key=lambda x: -rel_order(x[0]) if (x[0].startswith('snt') or x[0].startswith('op')) else -1)
                else:
                    self.undirected_edges[src].sort(key=lambda x: -rel_order(x[0]))
            for rel, des in self.undirected_edges[src]:
                if des in visited:
                    continue
                else:
                    queue.append(des)
                    visited.add(des)
        
        not_connected = len(queue) != len(self.nodes)
        assert (not not_connected)
        not_connected = False
        name2pos = dict(zip(queue, range(len(queue))))

        visited = set()
        edge = []
        for x in queue:
            if x not in self.undirected_edges:
                continue
            for r, y in self.undirected_edges[x]:
                if y in visited:
                    r = r[:-9] if r.endswith('_reverse_') else r + '_reverse_'
                    edge.append((name2pos[x], name2pos[y], r))  # x -> y: r
            visited.add(x)
        
        return [self.name2concept[x] for x in queue], edge, not_connected

    def to_levi(self, rel_order=None, shuffle=True):
        dependencies = defaultdict(set)
        name2instance = dict()
        name2instance.update(self.name2concept)
        for u, rs in self.edges.items():
            for r, v in rs:
                # u --r--> v
                r = REL + r
                r_name = f'rel_{len(name2instance)}'
                name2instance[r_name] = r
                dependencies[v].add(r_name)
                dependencies[r_name].add(u)
        gs = []
        try:
            for g in toposort(dependencies):
                gs.append(g)
        except CircularDependencyError:
            pass
            # self.visualize()
            # print('Cyclic graph detected, maybe caused by the reversing script.')
        node_seq = []
        for g in gs:
            g = list(g)
            if rel_order:
                if shuffle:
                    if random.random() < 0.5:
                        g = sorted(g, key=lambda x: -rel_order(name2instance[x]) if (
                                name2instance[x].startswith('snt') or name2instance[x].startswith('op')) else -1)
                    else:
                        random.shuffle(g)
                else:
                    g = sorted(g, key=lambda x: -rel_order(name2instance[x]))
            node_seq += g
        ind = dict(map(reversed, enumerate(node_seq)))
        edge = []
        for v, us in dependencies.items():
            if v not in ind:
                continue
            for u in us:
                if u not in ind:
                    continue
                edge.append((ind[v], ind[u], ''))
        return [name2instance[x] for x in node_seq], edge

    def visualize(self, name='sig_ace'):
        
        G = nx.DiGraph()

        for u, rs in self.edges.items():

            for r, v in rs:
                G.add_node(u, label=self.name2concept[u])
                G.add_node(v, label=self.name2concept[v])
                #if u!='root':
                G.add_edge(u, v, label=r)
        A = to_agraph(G)
        A.layout('dot')
        png = f'file_path'
        A.draw(png)
        os.system(f'open {png}')


class SIGGraph_orignal(object):

    def __init__(self, smatch_sig):
        # transform sig from original smatch format into our own data structure
        instance_triple, attribute_triple, relation_triple = smatch_sig.get_triples()
        self.root = smatch_sig.root
        self.nodes = set()
        self.edges = dict()
        self.reversed_edges = dict()
        self.undirected_edges = dict()
        self.name2concept = dict()

        # will do some adjustments
        self.abstract_concepts = dict()
        for _, name, concept in instance_triple:
            if is_attr_or_abs_form(concept):
                if _is_abs_form(concept):
                    self.abstract_concepts[name] = concept
                else:
                    pass
                    # print ('bad concept', _, name, concept)
            self.name2concept[name] = concept
            self.nodes.add(name)
        for rel, concept, value in attribute_triple:
            if rel == 'TOP':
                continue
            # discard some empty names
            if rel == 'name' and discard_regexp.match(value):
                continue
            # abstract concept can't have an attribute
            if concept in self.abstract_concepts:
                # print (rel, self.abstract_concepts[concept], value, "abstract concept cannot have an attribute")
                continue
            name = "%s_attr_%d" % (value, len(self.name2concept))
            if not _is_attr_form(value):
                if _is_abs_form(value):
                    self.abstract_concepts[name] = value
                else:
                    # print ('bad attribute', rel, concept, value)
                    continue
            self.name2concept[name] = value
            self._add_edge(rel, concept, name)
        for rel, head, tail in relation_triple:
            self._add_edge(rel, head, tail)

        # lower concept
        for name in self.name2concept:
            v = self.name2concept[name]
            if not _is_abs_form(v):
                v = v.lower()
            self.name2concept[name] = v

    def __len__(self):
        return len(self.name2concept)

    def _add_edge(self, rel, src, des):
        self.nodes.add(src)
        self.nodes.add(des)
        self.edges[src] = self.edges.get(src, []) + [(rel, des)]
        self.reversed_edges[des] = self.reversed_edges.get(des, []) + [(rel, src)]
        self.undirected_edges[src] = self.undirected_edges.get(src, []) + [(rel, des)]
        self.undirected_edges[des] = self.undirected_edges.get(des, []) + [(rel + '_reverse_', src)]

    def root_centered_sort(self, rel_order=None, shuffle=True):
        queue = [self.root]
        visited = set(queue)
        step = 0
        while len(queue) > step:
            src = queue[step]
            step += 1
            if src not in self.undirected_edges:
                continue
            if shuffle:
                random.shuffle(self.undirected_edges[src])
            if rel_order is not None:
                # Do some random thing here for performance enhancement
                if shuffle and random.random() < 0.5:
                    self.undirected_edges[src].sort(
                        key=lambda x: -rel_order(x[0]) if (x[0].startswith('snt') or x[0].startswith('op')) else -1)
                else:
                    self.undirected_edges[src].sort(key=lambda x: -rel_order(x[0]))
            for rel, des in self.undirected_edges[src]:
                if des in visited:
                    continue
                else:
                    queue.append(des)
                    visited.add(des)
        not_connected = len(queue) != len(self.nodes)
        assert (not not_connected)
        name2pos = dict(zip(queue, range(len(queue))))

        visited = set()
        edge = []
        for x in queue:
            if x not in self.undirected_edges:
                continue
            for r, y in self.undirected_edges[x]:
                if y in visited:
                    r = r[:-9] if r.endswith('_reverse_') else r + '_reverse_'
                    edge.append((name2pos[x], name2pos[y], r))  # x -> y: r
            visited.add(x)
        return [self.name2concept[x] for x in queue], edge, not_connected

    def to_levi(self, rel_order=None, shuffle=True):
        dependencies = defaultdict(set)
        name2instance = dict()
        name2instance.update(self.name2concept)
        for u, rs in self.edges.items():
            for r, v in rs:
                # u --r--> v
                r = REL + r
                r_name = f'rel_{len(name2instance)}'
                name2instance[r_name] = r
                dependencies[v].add(r_name)
                dependencies[r_name].add(u)
        gs = []
        try:
            for g in toposort(dependencies):
                gs.append(g)
        except CircularDependencyError:
            pass
            # self.visualize()
            # print('Cyclic graph detected, maybe caused by the reversing script.')
        node_seq = []
        for g in gs:
            g = list(g)
            if rel_order:
                if shuffle:
                    if random.random() < 0.5:
                        g = sorted(g, key=lambda x: -rel_order(name2instance[x]) if (
                                name2instance[x].startswith('snt') or name2instance[x].startswith('op')) else -1)
                    else:
                        random.shuffle(g)
                else:
                    g = sorted(g, key=lambda x: -rel_order(name2instance[x]))
            node_seq += g
        ind = dict(map(reversed, enumerate(node_seq)))
        edge = []
        for v, us in dependencies.items():
            if v not in ind:
                continue
            for u in us:
                if u not in ind:
                    continue
                edge.append((ind[v], ind[u], ''))
        return [name2instance[x] for x in node_seq], edge

    def visualize(self, name='sig_test_predict'):
        
        G = nx.DiGraph()
    
        for u, rs in self.edges.items():

            for r, v in rs:
                G.add_node(u, label=self.name2concept[u])
                G.add_node(v, label=self.name2concept[v])
                if self.name2concept[u]!='root':
                    G.add_edge(u, v, label=r)
        A = to_agraph(G)
        A.layout('dot')
        png = f'file_path'
        A.draw(png)
        os.system(f'open {png}')