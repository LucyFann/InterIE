

def match(output_file, input_file):
    block = []
    blocks = []
    for line in open(input_file, encoding='utf8').readlines():
        if line.startswith('#'):
            block.append(line)
        else:
            if block:
                blocks.append(block)
            block = []
    '''
    blocks[0]['# ::id bolt12_64545_0526.1 ::date 2012-12-23T18:47:13 ::annotator SDL-SIG-09 ::preferred\n', '# ::snt LOS ANGELES, May 2 (AFP)\n', '# ::tokens ["LOS", "ANGELES", ",", "May", "2", "(", "AFP", ")"]\n', '# ::lemmas ["LOS", "ANGELES", ",", "May", "2", "(", "AFP", ")"]\n', '# ::pos_tags ["NNP", "NNP", ",", "NNP", "CD", "-LRB-", "NNP", "-RRB-"]\n', '# ::ner_tags ["B-GPE", "E-GPE", "O", "B-DATE", "E-DATE", "O", "S-ORG", "O"]\n', "# ::entity_type ['B-GPE', 'E-GPE', 'O', 'O', 'O', 'O', 'S-ORG', 'O']\n", "# ::trigger ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']\n", '# ::save-date Fri Nov 3, 2017 ::file bolt12_64545_0526_1.txt\n']
    '''
    block1 = []
    blocks1 = []
    for line in open(output_file, encoding='utf8').readlines():
        if not line.startswith('#'):
            block1.append(line)
        else:
            if block1:
                blocks1.append(block1) 
            block1 = []
    if block1:
        blocks1.append(block1)
    assert len(blocks) == len(blocks1), (len(blocks), len(blocks1))


    with open(output_file+'.pred', 'w', encoding='utf8') as fo:
        for block, block1 in zip(blocks, blocks1):
            for line in block:
                fo.write(line)
            for line in block1:
                fo.write(line)
