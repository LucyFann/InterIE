
import numpy as np

import torch
from torch import nn
import torch.nn.functional as F
import re
from sig_parser.transformer import Embedding


def SIGEmbedding(vocab, embedding_dim, pretrained_file=None, sig=False, dump_file=None):
 
    if pretrained_file is None:
     
        return Embedding(vocab.size, embedding_dim, vocab.padding_idx)
    tokens_to_keep = set()
    for idx in range(vocab.size):
        token = vocab.idx2token(idx)
        if sig:
            token = re.sub(r'-\d\d$', '', token)
        tokens_to_keep.add(token)

    embeddings = {}
 
    if dump_file is not None:
        fo = open(dump_file, 'w', encoding='utf8')

    with open(pretrained_file, encoding='utf8') as embeddings_file:
        for line in embeddings_file.readlines():    
            fields = line.rstrip().split(' ')
            if len(fields) - 1 != embedding_dim:
                continue
            token = fields[0]
            if token in tokens_to_keep:
                if dump_file is not None:
                    fo.write(line)
                vector = np.asarray(fields[1:], dtype='float32')
                embeddings[token] = vector

    if dump_file is not None:
        fo.close()

    all_embeddings = np.asarray(list(embeddings.values()))
    print('pretrained', all_embeddings.shape)
    embeddings_mean = float(np.mean(all_embeddings))
    embeddings_std = float(np.std(all_embeddings))
    all_embeddings -= embeddings_mean
    all_embeddings /= embeddings_std
    all_embeddings *= 0.02
    embeddings_mean = float(np.mean(all_embeddings))
    embeddings_std = float(np.std(all_embeddings))
    print(embeddings_mean, embeddings_std)
    # Now we initialize the weight matrix for an embedding layer, starting with random vectors,
    # then filling in the word vectors we just read.
    embedding_matrix = torch.FloatTensor(vocab.size, embedding_dim).normal_(embeddings_mean,
                                                                            embeddings_std)
    for i in range(vocab.size):
        token = vocab.idx2token(i)

        # If we don't have a pre-trained vector for this word, we'll just leave this row alone,
        # so the word has a random initialization.
        if token in embeddings:
            embedding_matrix[i] = torch.FloatTensor(embeddings[token])
        else:
            if sig:
                normalized_token = re.sub(r'-\d\d$', '', token)
                if normalized_token in embeddings:
                    embedding_matrix[i] = torch.FloatTensor(embeddings[normalized_token])
    embedding_matrix[vocab.padding_idx].fill_(0.)

    return nn.Embedding.from_pretrained(embedding_matrix, freeze=False)

class WordEncoder(nn.Module):
    def __init__(self, vocabs, char_dim, word_dim, pos_dim, ner_dim, entity_type_dim,
                 trigger_type_dim, embed_dim, filters, char2word_dim,
                 dropout, pretrained_file=None):
        super(WordEncoder, self).__init__()
        self.char_embed = SIGEmbedding(vocabs['word_char'], char_dim)
        # character level features
        self.char2word = CNNEncoder(filters, char_dim, char2word_dim)
        self.lem_embed = SIGEmbedding(vocabs['lem'], word_dim, pretrained_file)
        if pos_dim > 0:
            self.pos_embed = SIGEmbedding(vocabs['pos'], pos_dim)
        else:
            self.pos_embed = None
        if ner_dim > 0:
            self.ner_embed = SIGEmbedding(vocabs['ner'], ner_dim)
        else:
            self.ner_embed = None
        if entity_type_dim > 0:
            self.entity_type_embed = SIGEmbedding(vocabs['entity_type'], entity_type_dim)
        else:
            self.entity_type_embed = None

        '''
        if entity_subtype_dim > 0:
            self.entity_subtype_embed = SIGEmbedding(vocabs['entity_subtype'], entity_subtype_dim)
        else:
            self.entity_subtype_embed = None
        if mention_type_dim > 0:
            self.mention_type_embed = SIGEmbedding(vocabs['mention_type'], mention_type_dim)
        else:
            self.mention_type_embed = None
        '''
        if trigger_type_dim > 0:
            self.trigger_type_embed = SIGEmbedding(vocabs['trigger_type'], trigger_type_dim)
        else:
            self.trigger_type_embed = None

        tot_dim = word_dim + pos_dim + ner_dim + char2word_dim + entity_type_dim + trigger_type_dim
        self.out_proj = nn.Linear(tot_dim, embed_dim)
        self.dropout = dropout
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.out_proj.weight, std=0.02)
        nn.init.constant_(self.out_proj.bias, 0.)

    def forward(self, char_input, tok_input, lem_input, pos_input, ner_input, entity_type_input,  trigger_type_input):
        # char: seq_len x bsz x word_len
        # word, pos, ner: seq_len x bsz
        seq_len, bsz, _ = char_input.size()
        char_repr = self.char_embed(char_input.view(seq_len * bsz, -1))
        char_repr = self.char2word(char_repr).view(seq_len, bsz, -1)
        lem_repr = self.lem_embed(lem_input)
        reprs = [char_repr, lem_repr]
        if self.pos_embed is not None:
            pos_repr = self.pos_embed(pos_input)
            reprs.append(pos_repr)

        if self.entity_type_embed is not None:
            entity_type_repr = self.entity_type_embed(entity_type_input)
            reprs.append(entity_type_repr)

        if self.trigger_type_embed is not None:
            trigger_type_repr = self.trigger_type_embed(trigger_type_input)
            reprs.append(trigger_type_repr)
        if self.ner_embed is not None:
            ner_repr = self.ner_embed(ner_input)
            reprs.append(ner_repr)

        word = F.dropout(torch.cat(reprs, -1), p=self.dropout, training=self.training)
        word = self.out_proj(word)
        return word

class ConceptEncoder(nn.Module):
    def __init__(self, vocabs, char_dim, concept_dim, embed_dim, filters, char2concept_dim, dropout, pretrained_file=None):
        super(ConceptEncoder, self).__init__()
        self.char_embed = SIGEmbedding(vocabs['concept_char'], char_dim)
        self.concept_embed = SIGEmbedding(vocabs.get('concept_and_rel', vocabs['concept']), concept_dim,
                                          pretrained_file, sig=True)
        self.char2concept = CNNEncoder(filters, char_dim, char2concept_dim)
        self.vocabs = vocabs
        tot_dim = char2concept_dim + concept_dim
        self.out_proj = nn.Linear(tot_dim, embed_dim)
        self.char_dim = char_dim
        self.concept_dim = concept_dim
        self.dropout = dropout
        self.reset_parameters()


    def reset_parameters(self):
        nn.init.normal_(self.out_proj.weight, std=0.02)
        nn.init.constant_(self.out_proj.bias, 0.)

    def forward(self, char_input, concept_input):

        seq_len, bsz, _ = char_input.size()
        char_repr = self.char_embed(char_input.view(seq_len * bsz, -1))
        char_repr = self.char2concept(char_repr).view(seq_len, bsz, -1)
        concept_repr = self.concept_embed(concept_input)

        concept = F.dropout(torch.cat([char_repr, concept_repr], -1), p=self.dropout, training=self.training)
        concept = self.out_proj(concept)
        return concept



'''
#(['entity_type', 'event_type', 'relation_type', 'role_type', 'mention_type', 'entity_label', 'trigger_label'])
class EntityEncoder(nn.Module):
    def __init__(self, vocabs, char_dim, entity_type_dim, embed_dim, filters, char2entity_type_dim, dropout, pretrained_file=None):

        super(EntityEncoder, self).__init__()
        self.char_embed = SIGEmbedding(vocabs['word_char'], char_dim)
        self.entity_embed = SIGEmbedding(vocabs.get('entity_type', vocabs['entity_label']), entity_type_dim,
                                         pretrained_file, sig=True)
        self.char2concept = CNNEncoder(filters, char_dim, char2entity_type_dim)
        self.vocabs = vocabs
        tot_dim = char2entity_type_dim + entity_type_dim
        self.out_proj = nn.Linear(tot_dim, embed_dim)
        self.char_dim = char_dim
        self.entity_type_dim = entity_type_dim
        self.dropout = dropout
        self.reset_parameters()


    def reset_parameters(self):
        nn.init.normal_(self.out_proj.weight, std=0.02)
        nn.init.constant_(self.out_proj.bias, 0.)

    def forward(self, char_input, entity_input):

        seq_len, bsz, _ = char_input.size()
        char_repr = self.char_embed(char_input.view(seq_len * bsz, -1))
        char_repr = self.char2concept(char_repr).view(seq_len, bsz, -1)
        entity_repr = self.concept_embed(entity_input)

        entity = F.dropout(torch.cat([char_repr, entity_repr], -1), p=self.dropout, training=self.training)
        entity = self.out_proj(entity)
        return entity
'''


class CNNEncoder(nn.Module):
    def __init__(self, filters, input_dim, output_dim, highway_layers=1):
        super(CNNEncoder, self).__init__()
        self.convolutions = nn.ModuleList()
        for width, out_c in filters:
            self.convolutions.append(nn.Conv1d(input_dim, out_c, kernel_size=width))
        final_dim = sum(f[1] for f in filters)
        self.highway = Highway(final_dim, highway_layers)
        self.out_proj = nn.Linear(final_dim, output_dim)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.out_proj.weight, std=0.02)
        nn.init.constant_(self.out_proj.bias, 0.)

    def forward(self, input):
        # input: batch_size x seq_len x input_dim
        x  = input.transpose(1, 2)
        conv_result = []
        for i, conv in enumerate(self.convolutions):
            y = conv(x)
            y, _ = torch.max(y, -1)
            y = F.relu(y)
            conv_result.append(y)

        conv_result = torch.cat(conv_result, dim=-1)
        conv_result = self.highway(conv_result)
        return self.out_proj(conv_result) #  batch_size x output_dim

class Highway(nn.Module):
    def __init__(self, input_dim, layers):
        super(Highway, self).__init__()
        self.input_dim = input_dim
        self.layers = nn.ModuleList([nn.Linear(input_dim, input_dim * 2)
                                     for _ in range(layers)])
        self.reset_parameters()

    def reset_parameters(self):
        for layer in self.layers:
            nn.init.normal_(layer.weight, std=0.02)
            nn.init.constant_(layer.bias[self.input_dim:], 1)
            nn.init.constant_(layer.bias[:self.input_dim], 0)

    def forward(self, x):
        for layer in self.layers:
            new_x = layer(x)
            new_x, gate = new_x.chunk(2, dim=-1)
            new_x = F.relu(new_x)
            gate = torch.sigmoid(gate)
            x = gate * x + (1 - gate) * new_x
        return x

if __name__ == "__main__":
    from data import Vocab, CLS, DUM, END
    vocab= Vocab('../data/SIG/sig_1.0_reca/lem_vocab', 3, [CLS])
    embed = SIGEmbedding(vocab, 300, pretrained_file='../data/glove.840B.300d.txt', dump_file='../data/SIG/sig_1.0_reca/glove_lem_embed')
    vocab = Vocab('../data/SIG/sig_1.0_reca/concept_vocab', 3, [DUM, END])
    embed = SIGEmbedding(vocab, 300, pretrained_file='../data/glove.840B.300d.txt', sig=True, dump_file='../data/SIG/sig_1.0_reca/glove_concept_embed')

