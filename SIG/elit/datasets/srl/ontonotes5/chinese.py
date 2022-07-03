# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2020-11-26 16:07
import os
from urllib.error import HTTPError
import shutil

from elit.datasets.srl.ontonotes5 import ONTONOTES5_HOME, CONLL12_HOME
from elit.datasets.srl.ontonotes5._utils import make_gold_conll, make_ontonotes_language_jsonlines, \
    batch_make_ner_tsv_if_necessary
from elit.utils.io_util import get_resource, path_from_url
from elit.utils.log_util import cprint, flash

_ONTONOTES5_CHINESE_HOME = ONTONOTES5_HOME + 'files/data/chinese/'
_ONTONOTES5_CONLL12_CHINESE_HOME = CONLL12_HOME + 'chinese/'
ONTONOTES5_CONLL12_CHINESE_TRAIN = _ONTONOTES5_CONLL12_CHINESE_HOME + 'train.chinese.conll12.jsonlines'
'''Training set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''
ONTONOTES5_CONLL12_CHINESE_DEV = _ONTONOTES5_CONLL12_CHINESE_HOME + 'development.chinese.conll12.jsonlines'
'''Dev set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''
ONTONOTES5_CONLL12_CHINESE_TEST = _ONTONOTES5_CONLL12_CHINESE_HOME + 'test.chinese.conll12.jsonlines'
'''Test set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''

ONTONOTES5_CONLL12_NER_CHINESE_TRAIN = _ONTONOTES5_CONLL12_CHINESE_HOME + 'train.chinese.conll12.ner.tsv'
'''Training set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''
ONTONOTES5_CONLL12_NER_CHINESE_DEV = _ONTONOTES5_CONLL12_CHINESE_HOME + 'development.chinese.conll12.ner.tsv'
'''Dev set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''
ONTONOTES5_CONLL12_NER_CHINESE_TEST = _ONTONOTES5_CONLL12_CHINESE_HOME + 'test.chinese.conll12.ner.tsv'
'''Test set of OntoNotes5 used in CoNLL12 (:cite:`pradhan-etal-2012-conll`).'''

try:
    get_resource(ONTONOTES5_HOME, verbose=False)
except HTTPError:
    intended_file_path = path_from_url(ONTONOTES5_HOME)
    cprint('Ontonotes 5.0 is a [red][bold]copyright[/bold][/red] dataset owned by LDC which we cannot re-distribute. '
           f'Please apply for a licence from LDC (https://catalog.ldc.upenn.edu/LDC2016T13) '
           f'then download it to {intended_file_path}')
    cprint('Luckily, an [red]unofficial[/red] Chinese version is provided on GitHub '
           'which will be used for demonstration purpose.')
    unofficial_chinese = get_resource('https://github.com/GuocaiL/Coref_Resolution/archive/master.zip#data/')
    intended_home, _ = os.path.splitext(intended_file_path)
    intended_chinese = f'{intended_home}/data/files/data/chinese/'
    # print(os.path.dirname(intended_chinese))
    # print(unofficial_chinese)
    # print(intended_chinese)
    for folder in ['annotations', 'metadata']:
        flash(f'Copying {unofficial_chinese}{folder} to {intended_chinese}{folder} [blink][yellow]...[/yellow][/blink]')
        shutil.copytree(f'{unofficial_chinese}{folder}', f'{intended_chinese}{folder}')
    flash('')

try:
    get_resource(ONTONOTES5_CONLL12_CHINESE_TRAIN, verbose=False)
except HTTPError:
    make_gold_conll(ONTONOTES5_HOME + '..', 'chinese')
    make_ontonotes_language_jsonlines(CONLL12_HOME + 'v4', language='chinese')

batch_make_ner_tsv_if_necessary(
    [ONTONOTES5_CONLL12_CHINESE_TRAIN, ONTONOTES5_CONLL12_CHINESE_DEV, ONTONOTES5_CONLL12_CHINESE_TEST])
