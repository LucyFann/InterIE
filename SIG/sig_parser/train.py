import argparse
import os

import random
import time
import sys
sys.path.append(".") 
from elit.common.util import isdebugging
from elit.utils.log_util import cprint

if os.environ.get('USE_TF', None) is None:
    os.environ["USE_TF"] = 'NO'  # saves time loading transformers
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from elit.transform.transformer_tokenizer import TransformerSequenceTokenizer
from elit.utils.time_util import CountdownTimer
from sig_parser.adam import AdamWeightDecayOptimizer
from sig_parser.bert_utils import load_bert, BertEncoderTokenizer
from sig_parser.data import Vocab, DataLoader, DUM, END, CLS, NIL, seperate_concept_from_rel
from sig_parser.extract import LexicalMap
from sig_parser.parser import Parser
from sig_parser.postprocess import PostProcessor
from sig_parser.utils import move_to_device
from work import parse_data



def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tok_vocab', type=str)
    parser.add_argument('--lem_vocab', type=str)
    parser.add_argument('--pos_vocab', type=str)
    parser.add_argument('--ner_vocab', type=str)
    parser.add_argument('--concept_vocab', type=str)
    parser.add_argument('--predictable_concept_vocab', type=str)
    parser.add_argument('--rel_vocab', type=str)
    parser.add_argument('--word_char_vocab', type=str)
    parser.add_argument('--concept_char_vocab', type=str)
    parser.add_argument('--entity_type_vocab', type=str)
    parser.add_argument('--trigger_type_vocab', type=str)
    parser.add_argument('--pretrained_file', type=str, default=None)
    parser.add_argument('--with_bert', dest='with_bert', action='store_true')
    parser.add_argument('--joint_arc_concept', dest='joint_arc_concept', action='store_true')
    parser.add_argument('--levi_graph', dest='levi_graph', type=str, default=None)
    parser.add_argument('--separate_rel', dest='separate_rel', action='store_true')
    parser.add_argument('--extra_arc', dest='extra_arc', action='store_true')
    parser.add_argument('--bert_path', type=str, default=None)

    parser.add_argument('--word_char_dim', type=int)
    parser.add_argument('--word_dim', type=int)
    parser.add_argument('--pos_dim', type=int)
    parser.add_argument('--ner_dim', type=int)
    parser.add_argument('--entity_type_dim', type=int)
    parser.add_argument('--entity_subtype_dim', type=int)
    parser.add_argument('--mention_type_dim', type=int)
    parser.add_argument('--trigger_type_dim', type=int)
    parser.add_argument('--concept_char_dim', type=int)
    parser.add_argument('--concept_dim', type=int)
    parser.add_argument('--rel_dim', type=int)
    parser.add_argument('--cnn_filters', type=int, nargs='+')
    parser.add_argument('--char2word_dim', type=int)
    parser.add_argument('--char2concept_dim', type=int)
    parser.add_argument('--embed_dim', type=int)
    parser.add_argument('--ff_embed_dim', type=int)
    parser.add_argument('--num_heads', type=int)
    parser.add_argument('--snt_layers', type=int)
    parser.add_argument('--graph_layers', type=int)
    parser.add_argument('--inference_layers', type=int)

    parser.add_argument('--dropout', type=float)
    parser.add_argument('--unk_rate', type=float)

    parser.add_argument('--epochs', type=int)
    parser.add_argument('--max_batches_acm', type=int, default=60000)
    parser.add_argument('--train_data', type=str)
    parser.add_argument('--dev_data', type=str)
    parser.add_argument('--test_data', type=str)
    parser.add_argument('--train_batch_size', type=int)
    parser.add_argument('--batches_per_update', type=int)
    parser.add_argument('--dev_batch_size', type=int)
    parser.add_argument('--test_batch_size', type=int)
    parser.add_argument('--lr_scale', type=float)
    parser.add_argument('--warmup_steps', type=int)
    parser.add_argument('--resume_ckpt', type=str, default=None)
    parser.add_argument('--ckpt', type=str)
    parser.add_argument('--print_every', type=int)
    parser.add_argument('--eval_every', type=int)
    parser.add_argument('--seed', type=int, default=int(time.time()))

    parser.add_argument('--world_size', type=int)
    parser.add_argument('--gpus', type=int)
    parser.add_argument('--MASTER_ADDR', type=str)
    parser.add_argument('--MASTER_PORT', type=str)
    parser.add_argument('--start_rank', type=int)
    parser.add_argument('--ace_json', type=str)
    args = parser.parse_args()
    if args.levi_graph == 'true' or args.levi_graph == '1':
        args.levi_graph = 'kahn'
        args.joint_arc_concept = True
    else:
        args.joint_arc_concept = False
    print(f'levi_graph = {args.levi_graph}')
    print(f'joint_arc_concept = {args.joint_arc_concept}')
    return args


def average_gradients(model):
    size = float(dist.get_world_size())
    for param in model.parameters():
        if param.grad is not None:
            dist.all_reduce(param.grad.data, op=dist.ReduceOp.SUM)
            param.grad.data /= size


def update_lr(optimizer, lr_scale, embed_size, steps, warmup_steps):
    lr = lr_scale * embed_size ** -0.5 * min(steps ** -0.5, steps * (warmup_steps ** -1.5))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr


def data_proc(data, queue):
    while True:
        for x in data:
            queue.put(x)
        queue.put('EPOCHDONE')


def load_vocabs(args):
    vocabs = dict()
    # 第二个参数是最少出现数量
    #vocabs['entity_type'] = Vocab(args.entity_type_vocab, 5, [CLS])
    # vocabs['entity_subtype'] = Vocab(args.entity_subtype_vocab, 5, [CLS])
    # vocabs['mention_type'] = Vocab(args.mention_type_vocab, 5, [CLS])
    #vocabs['trigger_type'] = Vocab(args.trigger_type_vocab, 2, [CLS])
    vocabs['tok'] = Vocab(args.tok_vocab, 5, [CLS])
    vocabs['lem'] = Vocab(args.lem_vocab, 5, [CLS])
    vocabs['pos'] = Vocab(args.pos_vocab, 5, [CLS])
    vocabs['ner'] = Vocab(args.ner_vocab, 5, [CLS])
    vocabs['predictable_concept'] = Vocab(args.predictable_concept_vocab, 1, [DUM, END])
    vocabs['concept'] = Vocab(args.concept_vocab, 1, [DUM, END])
    vocabs['rel'] = Vocab(args.rel_vocab, 1, [NIL])
    vocabs['word_char'] = Vocab(args.word_char_vocab, 100, [CLS, END])
    vocabs['concept_char'] = Vocab(args.concept_char_vocab, 100, [CLS, END])

    lexical_mapping = LexicalMap()
    if args.separate_rel:
        seperate_concept_from_rel(vocabs)

    bert_encoder = None
    if args.with_bert:
        bert_tokenizer = BertEncoderTokenizer.from_pretrained(args.bert_path, do_lower_case=False)
        # tokenizer = TransformerSequenceTokenizer(args.bert_path, 'token', use_fast=False, do_basic_tokenize=False,
        #                                          cls_is_bos=True)
        vocabs['bert_tokenizer'] = bert_tokenizer
    for name in vocabs:
        if name == 'bert_tokenizer':
            continue
        print((name, vocabs[name].size, vocabs[name].coverage))
    return vocabs, lexical_mapping


def main(local_rank, args):

    vocabs, lexical_mapping = load_vocabs(args)
    bert_encoder = None
    if args.with_bert:
        bert_encoder = load_bert(args.bert_path)
    seed = args.seed
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    torch.cuda.set_device(local_rank)
    device = torch.device('cuda', local_rank)

    model = Parser(vocabs,
                   args.word_char_dim, args.word_dim, args.pos_dim, args.ner_dim,
                   args.entity_type_dim,
                   args.trigger_type_dim, args.concept_char_dim, args.concept_dim,
                   args.cnn_filters, args.char2word_dim, args.char2concept_dim,
                   args.embed_dim, args.ff_embed_dim, args.num_heads, args.dropout,
                   args.snt_layers, args.graph_layers, args.inference_layers, args.rel_dim,
                   args.pretrained_file, bert_encoder,
                   device, joint_arc_concept=args.joint_arc_concept, levi_graph=args.levi_graph)
    if args.world_size > 1:
        torch.manual_seed(seed + dist.get_rank())
        torch.cuda.manual_seed_all(seed + dist.get_rank())
        random.seed(seed + dist.get_rank())
 
    model = model.cuda(local_rank)


    dev_data = DataLoader(vocabs, lexical_mapping, args.dev_data, args.dev_batch_size, for_train=False,
                          levi_graph=args.levi_graph, extra_arc=args.extra_arc)

    test_data = DataLoader(vocabs, lexical_mapping, args.test_data, args.test_batch_size, for_train=False,
                          levi_graph=args.levi_graph, extra_arc=args.extra_arc)
    pp = PostProcessor(vocabs['rel'])

    weight_decay_params = []
    no_weight_decay_params = []
  
    for name, param in model.named_parameters():
        #print(name, ':', param.size())
        if name.endswith('bias') or 'layer_norm' in name:
            no_weight_decay_params.append(param)
        else:
            weight_decay_params.append(param)

    grouped_params = [{'params': weight_decay_params, 'weight_decay': 1e-4},
                      {'params': no_weight_decay_params, 'weight_decay': 0.}]

    optimizer = AdamWeightDecayOptimizer(grouped_params, 1., betas=(0.9, 0.999), eps=1e-6)

    used_batches = 0
    batches_acm = 0
    print(args.resume_ckpt)

    if args.resume_ckpt:
        print(f'Resume from {args.resume_ckpt}')
        ckpt = torch.load(args.resume_ckpt)
        model.load_state_dict(ckpt['model'])
        optimizer.load_state_dict(ckpt['optimizer'])
        batches_acm = ckpt['batches_acm']
        del ckpt
    train_data = DataLoader(vocabs,
                            lexical_mapping, args.train_data, args.train_batch_size, for_train=True,
                            levi_graph=args.levi_graph, extra_arc=args.extra_arc)

    train_data1 = DataLoader(vocabs,
                            lexical_mapping, args.train_data, args.train_batch_size, for_train=False,
                            levi_graph=args.levi_graph, extra_arc=args.extra_arc)


    train_data.set_unk_rate(args.unk_rate)
    debugging = isdebugging()
    if debugging:
   
        train_data_generator = iter(train_data)
    else:
        queue = mp.Queue(10)
        train_data_generator = mp.Process(target=data_proc, args=(train_data, queue))
        train_data_generator.start()

    cprint(f'Model will be saved in [red]{args.ckpt}[/red]')
    model.train()
    epoch, loss_avg, concept_loss_avg, arc_loss_avg, rel_loss_avg = 0, 0, 0, 0, 0
    max_batches_acm = args.max_batches_acm
    timer = CountdownTimer(max_batches_acm - batches_acm)
    shuffle_siblings = False
    while batches_acm < max_batches_acm:
        if not shuffle_siblings and batches_acm >= 3000 and train_data.shuffle_siblings:
        
            shuffle_siblings = True
            print('Switch to deterministic sibling order')
            queue.close()
            train_data_generator.terminate()
            train_data = DataLoader(vocabs, lexical_mapping, args.train_data, args.train_batch_size, for_train=True,
                                    shuffle_siblings=False, levi_graph=args.levi_graph, extra_arc=args.extra_arc)
            train_data.set_unk_rate(args.unk_rate)
            queue = mp.Queue(10)
            train_data_generator = mp.Process(target=data_proc, args=(train_data, queue))
            train_data_generator.start()
        if debugging:
            batch = next(train_data_generator)
        else:
            batch = queue.get()
        if isinstance(batch, str):
            epoch += 1
            print('epoch', epoch, 'done', 'batches', batches_acm)
        else:
            batch = move_to_device(batch, model.device)
           
            concept_loss, arc_loss, rel_loss, graph_arc_loss, entity_loss, trigger_loss = model(batch)        
            if args.levi_graph:
                if arc_loss > 10:
                    cprint(f'[red]'
                           f'WARNING: arc_loss = {float(arc_loss)} exploded! '
                           f'Please retrain {args.ckpt}'
                           f'[/red]')
                loss = concept_loss + arc_loss + entity_loss + trigger_loss
                #print("entity_loss", entity_loss)
                #print("trigger_loss",trigger_loss)
            else:
                #print("entity_loss", entity_loss)
                #print("trigger_loss",trigger_loss)
                loss = concept_loss + arc_loss + rel_loss + entity_loss + trigger_loss
            loss /= args.batches_per_update
            loss_value = loss.item()
            concept_loss_value = concept_loss.item()
            arc_loss_value = arc_loss.item()
            rel_loss_value = 0 if rel_loss is None else rel_loss.item()
            loss_avg = loss_avg * args.batches_per_update * 0.8 + 0.2 * loss_value
            concept_loss_avg = concept_loss_avg * 0.8 + 0.2 * concept_loss_value
            arc_loss_avg = arc_loss_avg * 0.8 + 0.2 * arc_loss_value
            rel_loss_avg = rel_loss_avg * 0.8 + 0.2 * rel_loss_value
            
            loss.backward()
            used_batches += 1
            if not (used_batches % args.batches_per_update == -1 % args.batches_per_update):
                continue
            batches_acm += 1
            if args.world_size > 1:
                average_gradients(model)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            lr = update_lr(optimizer, args.lr_scale, args.embed_dim, batches_acm, args.warmup_steps)
            optimizer.step()
            optimizer.zero_grad()
            timer.log('Train Epoch %d, LR %.6f, conc_loss %.3f, arc_loss %.3f, rel_loss %.3f' % (
                epoch, lr, concept_loss_avg, arc_loss_avg, rel_loss_avg), ratio_percentage=False)
            if batches_acm % args.print_every == -1 % args.print_every:
                # print ('Train Epoch %d, Batch %d, LR %.6f, conc_loss %.3f, arc_loss %.3f, rel_loss %.3f'%(epoch, batches_acm, lr, concept_loss_avg, arc_loss_avg, rel_loss_avg))
                model.train()
            if (
                    (batches_acm > 20000 and batches_acm%2000==0) or args.resume_ckpt is not None):
                model.eval()
               
                torch.save({'args': args,
                            'model': model.state_dict(),
                            'batches_acm': batches_acm,
                            'optimizer': optimizer.state_dict()},
                           '%s/epoch%d_batch%d' % (args.ckpt, epoch, batches_acm))

                parse_data(model, pp, dev_data, args.dev_data, '%s/epoch%d_batch%d_dev_out' % (args.ckpt, epoch, batches_acm), 'file_path')
                parse_data(model, pp, train_data1, args.train_data, '%s/epoch%d_batch%d_train_out' % (args.ckpt, epoch, batches_acm), 'file_path')
                parse_data(model, pp, test_data, args.test_data,
                           '%s/epoch%d_batch%d_test_out' % (args.ckpt, epoch, batches_acm),
                           'file_path')
                model.train()
    queue.close()
    train_data_generator.terminate()


def init_processes(local_rank, args, backend='nccl'):
    os.environ['MASTER_ADDR'] = args.MASTER_ADDR
    os.environ['MASTER_PORT'] = args.MASTER_PORT
    dist.init_process_group(backend, rank=args.start_rank + local_rank, world_size=args.world_size)
    main(local_rank, args)


if __name__ == "__main__":
    args = parse_config()

    if not os.path.exists(args.ckpt):
        os.mkdir(args.ckpt)
    assert len(args.cnn_filters) % 2 == 0
    args.cnn_filters = list(zip(args.cnn_filters[:-1:2], args.cnn_filters[1::2]))
    if args.world_size == 1 or True:
        main(0, args)
        exit(0)
    mp.spawn(init_processes, args=(args,), nprocs=args.gpus)

