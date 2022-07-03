

import torch
from torch import nn
import torch.nn.functional as F
from sig_parser.data import NIL, PAD
from sig_parser.utils import compute_f_by_tensor
from sig_parser.transformer import MultiheadAttention

from sig_parser.utils import label_smoothed_nll_loss
import pickle


class ArcGenerator(nn.Module):
    def __init__(self, vocabs, embed_dim, ff_embed_dim, num_heads, dropout):
        super(ArcGenerator, self).__init__()
        self.vocabs = vocabs
        self.arc_layer = MultiheadAttention(embed_dim, num_heads, dropout, weights_dropout=False)
        self.arc_layer_norm = nn.LayerNorm(embed_dim)
        self.fc1 = nn.Linear(embed_dim, ff_embed_dim)
        self.fc2 = nn.Linear(ff_embed_dim, embed_dim)
        self.ff_layer_norm = nn.LayerNorm(embed_dim)
        self.dropout = dropout

    def forward(self, outs, graph_state, graph_padding_mask, attn_mask, target_rel=None, work=False):
        x, arc_weight = self.arc_layer(outs, graph_state, graph_state,
                                       key_padding_mask=graph_padding_mask,
                                       attn_mask=attn_mask,
                                       need_weights='max')
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.arc_layer_norm(outs + x)
        residual = x
        x = F.relu(self.fc1(x))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.fc2(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        outs = self.ff_layer_norm(residual + x)

        if work:
            arc_ll = torch.log(arc_weight + 1e-12)
            return arc_ll, outs
        target_arc = torch.ne(target_rel, self.vocabs['rel'].token2idx(NIL))  # 0 or 1
        arc_mask = torch.eq(target_rel, self.vocabs['rel'].token2idx(PAD))
        pred = torch.ge(arc_weight, 0.5)
        if not self.training:
            print('arc p %.3f r %.3f f %.3f' % compute_f_by_tensor(pred, target_arc, arc_mask))
        arc_loss = F.binary_cross_entropy(arc_weight, target_arc.float(), reduction='none')
        arc_loss = arc_loss.masked_fill_(arc_mask, 0.).sum((0, 2))
        return arc_loss, outs

class ConceptGenerator(nn.Module):
    def __init__(self, vocabs, embed_dim, ff_embed_dim, conc_size, dropout):
        super(ConceptGenerator, self).__init__()
        self.alignment_layer = MultiheadAttention(embed_dim, 1, dropout, weights_dropout=False)
        self.alignment_layer_norm = nn.LayerNorm(embed_dim)
        self.fc1 = nn.Linear(embed_dim, ff_embed_dim)
        self.fc2 = nn.Linear(ff_embed_dim, embed_dim)
        self.ff_layer_norm = nn.LayerNorm(embed_dim)
        self.transfer = nn.Linear(embed_dim, conc_size)
        self.generator = nn.Linear(conc_size, vocabs['predictable_concept'].size)
        self.entity_fc = nn.Linear(conc_size, 25, bias=False)
        self.trigger_fc = nn.Linear(conc_size, 549, bias=False)
        self.diverter = nn.Linear(conc_size, 3)
        self.vocabs = vocabs
        self.dropout = dropout
        self.cross_entropy = nn.CrossEntropyLoss()
        self.reset_parameters()


    def reset_parameters(self):
        nn.init.normal_(self.transfer.weight, std=0.02)
        nn.init.normal_(self.diverter.weight, std=0.02)
        nn.init.normal_(self.generator.weight, std=0.02)
        nn.init.constant_(self.diverter.bias, 0.)
        nn.init.constant_(self.transfer.bias, 0.)
        nn.init.constant_(self.generator.bias, 0.)

    
    def forward(self, outs, snt_state, snt_padding_mask, copy_seq,
                target=None, src_entity=None, src_trigger=None, work=False):


        x, alignment_weight = self.alignment_layer(outs, snt_state, snt_state,
                                                   key_padding_mask=snt_padding_mask,
                                                   need_weights='one')
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = self.alignment_layer_norm(outs + x)
        residual = x

        x = F.relu(self.fc1(x))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.fc2(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        outs = self.ff_layer_norm(residual + x)
        # seq_len==tg_len
        seq_len, bsz, _ = outs.size()
        outs_concept = torch.tanh(self.transfer(outs))
        outs_concept = F.dropout(outs_concept, p=self.dropout, training=self.training)
 
        gen_gate, map_gate, copy_gate = F.softmax(self.diverter(outs_concept), -1).chunk(3, dim=-1)
        copy_gate = torch.cat([copy_gate, map_gate], -1)

        probs = gen_gate * F.softmax(self.generator(outs_concept), -1)
        tot_ext = 1 + copy_seq.max().item()
        vocab_size = probs.size(-1)
        if tot_ext - vocab_size > 0:
            ext_probs = probs.new_zeros((1, 1, tot_ext - vocab_size)).expand(seq_len, bsz, -1)
            probs = torch.cat([probs, ext_probs], -1)
        # copy_seq: src_len x bsz x 2
        # copy_gate: tgt_len x bsz x 2

        # alignment_weight: tgt_len x bsz x src_len
        # index: tgt_len x bsz x (src_len x 2)
        index = copy_seq.transpose(0, 1).contiguous().view(1, bsz, -1).expand(seq_len, -1, -1)
 
        copy_probs = (copy_gate.unsqueeze(2) * alignment_weight.unsqueeze(-1)).view(seq_len, bsz, -1)
        
        probs = probs.scatter_add_(-1, index, copy_probs)

        ll = torch.log(probs + 1e-12)
      
        if work:

            return ll, outs, alignment_weight, 0, 0

        if not self.training:
            _, pred = torch.max(ll, -1)
            total_concepts = torch.ne(target, self.vocabs['predictable_concept'].padding_idx)
            acc = torch.eq(pred, target).masked_select(total_concepts).float().sum().item()
            tot = total_concepts.sum().item()
            print('conc acc', acc / tot)
  
        concept_loss = -ll.gather(dim=-1, index=target.unsqueeze(-1)).squeeze(-1)
                            
        concept_mask = torch.eq(target, self.vocabs['predictable_concept'].padding_idx)
       
        concept_loss = concept_loss.masked_fill_(concept_mask, 0.).sum(0)

        return concept_loss, outs, alignment_weight, 0 , 0


class JointArcConceptGenerator(nn.Module):
    def __init__(self, vocabs, embed_dim, ff_embed_dim, conc_size, dropout, num_heads):
        super(JointArcConceptGenerator, self).__init__()
        self.concept_padding_idx = vocabs['predictable_concept'].get_idx(PAD)
        self.transformer_layer = MultiheadAttention(embed_dim, num_heads, dropout, weights_dropout=False)
        self.transformer_layer_norm = nn.LayerNorm(embed_dim)
        self.fc1 = nn.Linear(embed_dim, ff_embed_dim)
        self.fc2 = nn.Linear(ff_embed_dim, embed_dim)
        self.ff_layer_norm = nn.LayerNorm(embed_dim)
        self.transfer = nn.Linear(embed_dim, conc_size)
        self.generator = nn.Linear(conc_size, len(vocabs['predictable_concept']))
        self.entity_fc = nn.Linear(conc_size, 25, bias=False)
        self.trigger_fc = nn.Linear(conc_size, 549, bias=False)        
        self.separate_rel = 'concept_and_rel' in vocabs
        if self.separate_rel:
            self.concept_or_rel = nn.Linear(conc_size, 2)
            self.rel_generator = nn.Linear(conc_size, len(vocabs['rel']))
        self.diverter = nn.Linear(conc_size, 3)
        self.dropout = dropout
        self.rel_nil_idx = vocabs['rel'].get_idx(NIL)
        self.rel_pad_idx = vocabs['rel'].get_idx(PAD)
        self.cross_entropy = nn.CrossEntropyLoss()
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.transfer.weight, std=0.02)
        nn.init.normal_(self.diverter.weight, std=0.02)
        nn.init.normal_(self.generator.weight, std=0.02)
        nn.init.constant_(self.diverter.bias, 0.)
        nn.init.constant_(self.transfer.bias, 0.)
        nn.init.constant_(self.generator.bias, 0.)

    def forward(self, outs, state, mask, attn_mask, copy_seq, target=None, target_rel=None,
                src_entity=None, src_trigger=None, work=False):
        """

        Args:
          outs: A
          state: The Transformer representations for each word.
          mask:
          attn_mask:
          copy_seq: Stack of lemma and concept (which is simply lemma + _)
          target:  Target concept
          work:  (Default value = False)

        Returns:


        """
        x, alignment_weight = self.transformer_layer(outs, state, state,
                                                     key_padding_mask=mask,
                                                     attn_mask=attn_mask,
                                                     need_weights='all')
          
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.transformer_layer_norm(outs + x)
        residual = x
        x = F.relu(self.fc1(x))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.fc2(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        outs = self.ff_layer_norm(residual + x)
     
        src_len, bsz, _ = outs.size()
        # seq_len
        snt_len = copy_seq.size(0)

        if src_len > snt_len:
            src_len -= snt_len
            tgt_len = src_len
            snt_outs, concept_outs = outs[:-src_len, :, :], outs[-src_len:, :, :]
        else:
            tgt_len = state.size(0) - snt_len
            concept_outs = outs
        outs_concept = torch.tanh(self.transfer(concept_outs))
        outs_concept = F.dropout(outs_concept, p=self.dropout, training=self.training)

        gen_gate, map_gate, copy_gate = F.softmax(self.diverter(outs_concept), -1).chunk(3, dim=-1)
        copy_gate = torch.cat([copy_gate, map_gate], -1)

        probs = gen_gate * F.softmax(self.generator(outs_concept), -1)

        tot_ext = 1 + copy_seq.max().item()
        vocab_size = probs.size(-1)

        if tot_ext - vocab_size > 0:
            ext_probs = probs.new_zeros((1, 1, tot_ext - vocab_size)).expand(src_len, bsz, -1)
            probs = torch.cat([probs, ext_probs], -1)

        # copy_seq: src_len x bsz x 2
        # copy_gate: tgt_len x bsz x 2
        # alignment_weight: tgt_len x bsz x src_len
        # index: tgt_len x bsz x (src_len x 2)
        index = copy_seq.transpose(0, 1).contiguous().view(1, bsz, -1).expand(src_len, -1, -1)

        arc_weight = alignment_weight[1:, -src_len:, :, -tgt_len:]
        arc_weight, _ = torch.max(arc_weight, dim=0)

        alignment_weight = alignment_weight[:, -src_len:, :, :snt_len]
        alignment_weight = alignment_weight[0, :, :, :]
        copy_probs = (copy_gate.unsqueeze(2) * alignment_weight.unsqueeze(-1)).view(src_len, bsz, -1)
        probs = probs.scatter_add_(-1, index, copy_probs)

        # Switch: concept or rel?
        if self.separate_rel:
            concept_gate, rel_gate = F.softmax(self.concept_or_rel(outs_concept), -1).chunk(2, dim=-1)
            probs *= concept_gate
            rel_probs = rel_gate * F.softmax(self.rel_generator(outs_concept), -1)
            probs[:, :, vocab_size:vocab_size + rel_probs.size(-1)] = rel_probs

        ll = torch.log(probs + 1e-12)

        if work:
            arc_ll = torch.log(arc_weight + 1e-12)
  
            return ll, arc_ll, outs,  alignment_weight,0,0

        concept_loss = -ll.gather(dim=-1, index=target.unsqueeze(-1)).squeeze(-1)
        concept_mask = torch.eq(target, self.concept_padding_idx)
        concept_loss = concept_loss.masked_fill_(concept_mask, 0.).sum(0)

        assert self.training

        # _, pred = torch.max(ll, -1)
        # total_concepts = torch.ne(target, self.concept_padding_idx)
        # acc = torch.eq(pred, target).masked_select(total_concepts).float().sum().item()
        # tot = total_concepts.sum().item()
        # concept_loss = (concept_loss, acc, tot)

        target_arc = torch.ne(target_rel, self.rel_nil_idx)  # 0 or 1
        arc_mask = torch.eq(target_rel, self.rel_pad_idx)
        arc_loss = F.binary_cross_entropy(arc_weight, target_arc.float(), reduction='none')
        arc_loss = arc_loss.masked_fill_(arc_mask, 0.).sum((0, 2))


        return concept_loss, arc_loss, outs, alignment_weight, 0,0

# biaffine decoder
class RelationGenerator(nn.Module):

    def __init__(self, vocabs, embed_dim, rel_size, dropout):
        super(RelationGenerator, self).__init__()
        self.vocabs = vocabs
        self.transfer_head = nn.Linear(embed_dim, rel_size)
        self.transfer_dep = nn.Linear(embed_dim, rel_size)

        self.proj = nn.Linear(rel_size + 1, vocabs['rel'].size * (rel_size + 1))
        self.dropout = dropout
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.transfer_head.weight, std=0.02)
        nn.init.normal_(self.transfer_dep.weight, std=0.02)
        nn.init.normal_(self.proj.weight, std=0.02)

        nn.init.constant_(self.proj.bias, 0.)
        nn.init.constant_(self.transfer_head.bias, 0.)
        nn.init.constant_(self.transfer_dep.bias, 0.)

    def forward(self, outs, graph_state, target_rel=None, work=False):

        def get_scores(dep, head):
            head = torch.tanh(self.transfer_head(head))
            dep = torch.tanh(self.transfer_dep(dep))

            head = F.dropout(head, p=self.dropout, training=self.training)
            dep = F.dropout(dep, p=self.dropout, training=self.training)

            dep_num, bsz, _ = dep.size()
            head_num = head.size(0)

            bias_dep = dep.new_ones((dep_num, bsz, 1))
            bias_head = head.new_ones((head_num, bsz, 1))

            # seq_len x bsz x dim
            dep = torch.cat([dep, bias_dep], 2)
            head = torch.cat([head, bias_head], 2)

            # bsz x dep_num x vocab_size x dim
            dep = self.proj(dep).view(dep_num, bsz, self.vocabs['rel'].size, -1).transpose(0, 1).contiguous()
            # bsz x dim x head_num
            head = head.permute(1, 2, 0)

            # bsz x dep_num x vocab_size x head_num
            scores = torch.bmm(dep.view(bsz, dep_num * self.vocabs['rel'].size, -1), head).view(bsz, dep_num,
                                                                                                self.vocabs['rel'].size,
                                                                                                head_num)
            return scores

        scores = get_scores(outs, graph_state).permute(1, 0, 3, 2).contiguous()

        dep_num, bsz, _ = outs.size()
        head_num = graph_state.size(0)
        log_probs = F.log_softmax(scores, dim=-1)
        _, rel = torch.max(log_probs, -1)
        if work:
            # dep_num x bsz x head x vocab
            return log_probs

        rel_mask = torch.eq(target_rel, self.vocabs['rel'].token2idx(NIL)) + torch.eq(target_rel,
                                                                                      self.vocabs['rel'].token2idx(PAD))
        rel_acc = (torch.eq(rel, target_rel).float().masked_fill_(rel_mask, 0.)).sum().item()
        rel_tot = rel_mask.numel() - rel_mask.float().sum().item()
        if not self.training:
            print('rel acc %.3f' % (rel_acc / rel_tot))
        rel_loss = label_smoothed_nll_loss(log_probs.view(-1, self.vocabs['rel'].size), target_rel.view(-1), 0.).view(
            dep_num, bsz, head_num)
        rel_loss = rel_loss.masked_fill_(rel_mask, 0.).sum((0, 2))
        return rel_loss



class DecodeLayer(nn.Module):

    def __init__(self, vocabs, inference_layers, embed_dim, ff_embed_dim, num_heads, conc_size, rel_size, dropout,
                 joint_arc_concept=False, external_biaffine=False, n_mlp_arc=500, levi_graph=False):
        super(DecodeLayer, self).__init__()
        self.external_biaffine = external_biaffine
        self.inference_iterations = inference_layers
     
        self.joint_arc_concept = joint_arc_concept
        if joint_arc_concept:
            self.arc_concept_generator = JointArcConceptGenerator(vocabs, embed_dim, ff_embed_dim, conc_size, dropout,
                                                                  num_heads)
        else:
            self.arc_generator = ArcGenerator(vocabs, embed_dim, ff_embed_dim, num_heads, dropout)
           
            self.concept_generator = ConceptGenerator(vocabs, embed_dim, ff_embed_dim, conc_size, dropout)
        self.levi_graph = levi_graph
        if not levi_graph:
            self.relation_generator = RelationGenerator(vocabs, embed_dim, rel_size, dropout)
        self.dropout = dropout
        self.vocabs = vocabs

   
    def forward(self, probe, snt_state, graph_state,
                snt_padding_mask, graph_padding_mask, attn_mask,
                copy_seq, target=None, target_rel=None, src_entity=None, src_trigger=None,
                work=False):
        # probe: tgt_len x bsz x embed_dim
        # snt_state, graph_state: seq_len x bsz x embed_dim

        outs = F.dropout(probe, p=self.dropout, training=self.training)
        if work is None:
            work = not self.training

        # if work:
            #for i in range(self.inference_iterations):
                 #arc_ll, outs = self.arc_generator(outs, graph_state, graph_padding_mask, attn_mask, work=True)
                 #concept_ll, outs, alignment_weight = self.concept_generator(outs, snt_state, snt_padding_mask, copy_seq, work=True)
            #rel_ll = self.relation_generator(outs, graph_state, work=True)
            #return concept_ll, arc_ll, rel_ll, alignment_weight


        # print("seqlen x bsz", snt_state.size())
        # print("copy_seq size",copy_seq.size())
        # print("concept_len x bsz", graph_state.size())
        # print("out size", outs.size())
        arc_losses, concept_losses, rel_losses, alignment_weightt = [], [], [], []
        if self.joint_arc_concept:
            device = snt_state.device
            snt_len, concept_len, bsz = snt_state.size(0), graph_state.size(0), graph_state.size(1)
            state = torch.cat([snt_state, graph_state], dim=0)
            if graph_padding_mask is None:
                graph_padding_mask = torch.zeros((concept_len, bsz), device=device, dtype=torch.bool)
            mask = torch.cat([snt_padding_mask, graph_padding_mask], dim=0)
            if attn_mask is not None:
                left = torch.zeros((snt_len + concept_len, snt_len), dtype=torch.bool, device=device)
                upper_right = torch.ones((snt_len, concept_len), dtype=torch.bool, device=device)
                right = torch.cat([upper_right, attn_mask], dim=0)
                attn_mask = torch.cat([left, right], dim=1)
            for i in range(self.inference_iterations):
                concept_loss, arc_loss, outs, alignment_weight, entity_loss, trigger_loss = self.arc_concept_generator(outs, state, mask, attn_mask, copy_seq,
                                                                          target=target, target_rel=target_rel,src_entity=src_entity,
                                                                          src_trigger=src_trigger, work=work)
                concept_losses.append(concept_loss)
                arc_losses.append(arc_loss)
                alignment_weightt.append(alignment_weight)
            outs = outs[-concept_len:, :, :]
        else:
            
            for i in range(self.inference_iterations):
                arc_loss, outs = self.arc_generator(outs, graph_state, graph_padding_mask, attn_mask,
                                                    target_rel=target_rel,
                                                    work=work)
                concept_loss, outs, alignment_weight, entity_loss, trigger_loss = self.concept_generator(outs, snt_state, snt_padding_mask,
                                                                              copy_seq, target=target, src_entity=src_entity,
                                                                              src_trigger=src_trigger, work=work)

                arc_losses.append(arc_loss)
                concept_losses.append(concept_loss)
                alignment_weightt.append(alignment_weight)
        if self.external_biaffine:
            arc_loss, rel_loss = self.biaffine(outs, graph_state, target_rel=target_rel, work=work)
        else:
            if self.levi_graph:
                rel_loss = None
            else:
                rel_loss = self.relation_generator(outs, graph_state, target_rel=target_rel, work=work)
            arc_loss = arc_losses[-1]  # torch.stack(arc_losses).mean(0)
        concept_loss = concept_losses[-1]  # torch.stack(concept_losses).mean(0)

        if work:
            return concept_loss, arc_loss, rel_loss, alignment_weightt[-1]
        else:
            return concept_loss, arc_loss, rel_loss, alignment_weightt[-1], entity_loss, trigger_loss



