#!/usr/bin/env python
#coding=utf-8

'''
Definition of Alignments class. For each sentence, computes the list of node variables that are aligned 
to each index in the sentence, assuming alignments in the format returned by JSIG 

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import smatch.sig_edited as sig_annot
from collections import defaultdict

class Alignments:

	def _traverse(self, parsed_sig, sig):
		triples = parsed_sig.get_triples3()
		triples2 = []
		root = None
		for i in range (0, len(triples)):
			rel = triples[i]
			if rel[1] == "TOP":
				triples2.append(("TOP",":top",rel[0]))
				root = rel[0]
			elif rel not in [r for r in parsed_sig.reent if r[2] in parsed_sig.nodes]:
				triples2.append((rel[0],":" + rel[1],rel[2]))
		indexes = {}
		queue = []
		visited = []
		queue.append((root, "0"))
		while len(queue) > 0:
			(node, prefix) = queue.pop(0)
			if node in visited:
				continue
			indexes[prefix] = node
			if node in parsed_sig.nodes:
				visited.append(node)
				children = [t for t in triples2 if str(t[0]) == node]
				i = 0
				for c in children:
					v = str(c[2])
					queue.append((v, prefix + "." + str(i)))
					i += 1
		return indexes


	def __init__(self, alignments_filename, graphs):
		self.alignments = []
		for g, line in zip(graphs,open(alignments_filename)):
			sig = g.strip()
			parsed_sig = sig_annot.SIG.parse_SIG_line(sig.replace("\n",""), False)
			line = line.strip()
			indexes = self._traverse(parsed_sig, sig)
			al = defaultdict(list)
			if line != "":
				for a in line.split(" "):
					if a.strip() == "":
						continue
					start = a.split("|")[0].split("-")[0]
					if start[0] == "*":
						start = start[1:]
					end = a.split("|")[0].split("-")[1]
					for i in range(int(start),int(end)):
						for segment in a.split("|")[1].split("+"):
							al[i].append(indexes[segment])
			self.alignments.append(al)
