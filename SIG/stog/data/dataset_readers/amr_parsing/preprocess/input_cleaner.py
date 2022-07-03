import re

from word2number import w2n


ORDINAL_MAP = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 5,
    'sixth': 6,
    'seventh': 7,
    'eighth': 8,
    'ninth': 9
}


DECADE_MAP = {
    'twenties': 20,
    'thirties': 30,
    'forties': 40,
    'fifties': 50,
    'sixties': 60,
    'seventies': 70,
    'eighties': 80,
    'nineties': 90
}


def clean(sig):
    correct_errors(sig)
    normalize_tokens(sig)
    # Named entity
    join_model_name(sig)
    split_entity_with_slash(sig)
    split_entity_with_non(sig)
    split_entity_prefix(sig, 'anti')
    split_entity_prefix(sig, 'ex')
    split_entity_prefix(sig, 'cross')
    split_entity_prefix(sig, 'pro')
    replace_NT_dollar_abbr(sig)
    # Date
    join_time_description(sig)
    split_date_duration(sig)
    split_numerical_date(sig)
    split_year_month(sig)
    split_era(sig)
    split_911(sig)
    split_ratio(sig)
    split_unit_with_number(sig)
    split_number_with_dash_prefix(sig)


def correct_errors(sig):
    while True:
        index = None
        for i, token in enumerate(sig.tokens):
            if token == '570000':
                index = i
                tokens = ['2005', '07']
                pos = ['CD', 'CD']
                ner = ['DATE', 'DATE']
                break
            if token == '990000':
                index = i
                tokens = ['1999'] if sig.id.startswith('PROXY_AFP_ENG') else ['1990']
                pos = ['CD']
                ner = ['DATE']
                break
            if token == '860000':
                index = i
                tokens = ['1986']
                pos = ['CD']
                ner = ['DATE']
                break
            if token == '-20040824':
                index = i
                tokens = ['2004', '07', '24']
                pos = ['CD', 'CD', 'CD']
                ner = ['DATE', 'DATE', 'DATE']
                break
            if sig.id.startswith('PROXY_XIN_ENG_20030709_0070.6') and token == 'July':
                index = i
                tokens = ['June']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_APW_ENG_20080826_0891.5') and token == 'August':
                index = i
                tokens = ['July']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_LTW_ENG_20070514_0055.19') and token == 'May':
                index = i
                tokens = ['March']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070430_0038.8') and token == 'February':
                index = i
                tokens = ['April']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070504_0296.10') and token == '070513':
                index = i
                tokens = ['20130513']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070504_0296.10') and token == '070514':
                index = i
                tokens = ['20130514']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070607_0366.8') and token == 'April':
                index = i
                tokens = ['June']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070612_0538.6') and token == 'June':
                index = i
                tokens = ['December']
                pos = ['NNP']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070612_0538.6') and token == '12':
                index = i
                tokens = ['6']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070620_0032.14') and token == 'June':
                index = i
                tokens = ['6']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070906_0523') and token == 'September':
                index = i
                tokens = ['9']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070910_0544') and token == 'September':
                index = i
                tokens = ['9']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20071204_0145.25') and token == '200':
                index = i
                tokens = ['2000']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20071206_0630.5') and token == 'November':
                index = i
                tokens = ['10']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_APW_ENG_20080112_0264.5') and token == '080112':
                index = i
                tokens = ['20081112']
                pos = ['CD']
                ner = ['DATE']
                break
            if sig.id.startswith('PROXY_XIN_ENG_20021123_0156.20') and token == 'a-third-party':
                index = i
                tokens = ['a', 'third', 'party']
                pos = ['DT', 'JJ', 'NN']
                ner = ['O', 'ORDINAL', 'O']
                break
            if sig.id.startswith('DF-225-195986-849_0460.9') and token == '2most':
                index = i
                tokens = ['2', 'most']
                pos = ['CD', 'JJS']
                ner = ['ORDINAL', 'O']
                break
            if sig.id.startswith('DF-200-192400-625_7557.16') and token == 'what':
                index = i
                tokens = ['want']
                pos = ['VBP']
                ner = ['O']
                break
            if sig.id.startswith('DF-200-192392-456_1160.5') and token == 'couting':
                index = i
                tokens = ['count']
                pos = ['VBG']
                ner = ['O']
                break
            if sig.id.startswith('bolt-eng-DF-170-181103-8882248_0182.50') and token == '31:10-31':
                index = i
                tokens = ['31', ':', '10', '-', '31']
                pos = ['CD', ':', 'CD', ':', 'CD']
                ner = ['ORDINAL', 'O', 'O', 'O', 'O']
                break
            if ((sig.id.startswith('PROXY_AFP_ENG_20071030_0313.5') or
                 sig.id.startswith('PROXY_AFP_ENG_20071030_0313.10'))
                    and token == 'approximately'):
                index = i
                tokens = []
                pos = []
                ner = []
                break
            if sig.id.startswith('PROXY_AFP_ENG_20050603_0056.11') and token == 'first' and sig.tokens[i - 1] == "'s":
                index = i
                tokens = ['firstly', 'first']
                pos = ['NN', 'NN']
                ner = ['ORDINAL', 'O']
                break
            if sig.id.startswith('PROXY_AFP_ENG_20070327_0002.14') and token == 'first' and sig.tokens[i + 1] == 'time':
                index = i
                tokens = ['first', 'firstly']
                pos = ['NN', 'JJ']
                ner = ['O', 'ORDINAL']
                break
            if sig.id.startswith('DF-200-192400-625_7046.5') and token == 'my' and sig.tokens[i + 1] == 'counsellers':
                index = i
                tokens = ['my', '2']
                pos = ['PRP$', 'CD']
                ner = ['O', 'NUMBER']
                break
            if sig.id.startswith('PROXY_LTW_ENG_20081115_0076.19') and token == 'a' and sig.tokens[i + 1] == 'year':
                index = list(range(i, i + 5))
                tokens = ['1.5', 'year']
                pos = ['CD', 'NN']
                ner = ['NUMBER', 'DURATION']
                break
            if sig.id.startswith('PROXY_XIN_ENG_20020905_0122.11') and token == 'separate' and sig.tokens[i + 1] == 'bomb':
                index = list(range(i, i + 2))
                tokens = ['separate', 'two', 'bomb']
                pos = ['JJ', 'CD', 'JJ']
                ner = ['O', 'NUMBER', 'O']
                break
            if (token == 'second' and i + 2 < len(sig.tokens) and
                    sig.tokens[i + 1] == 'to' and sig.tokens[i + 2] == 'last'):
                index = [i, i + 1, i + 2]
                tokens = ['-2']
                pos = ['CD']
                ner = ['ORDINAL']
                break
            if token.lower() == 'tonight':
                index = i
                tokens = ['today', 'night']
                pos = ['NN', 'NN']
                ner = ['DATE', 'DATE']
                break
            if token == '1ps':
                index = i
                tokens = ['1', 'pence']
                pos = ['CD', 'NN']
                ner = ['NUMBER', 'O']
                break
        else:
            break
        if not isinstance(index, list):
            index = [index]
        sig.replace_span(index, tokens, pos, ner)


def normalize_tokens(sig):
    while True:
        span = None
        for i, lemma in enumerate(sig.lemmas):
            lemma_lower = lemma.lower()
            token_lower = sig.tokens[i].lower()
            if lemma_lower == 'midnight':
                span = [i]
                tokens = ['0:00']
                pos = ['CD']
                ner = ['TIME']
                break
            if token_lower in DECADE_MAP:
                span = [i]
                tokens = [str(DECADE_MAP[token_lower])]
                pos = ['CD']
                ner = ['TIME']
                break
            if lemma_lower in ORDINAL_MAP:
                span = [i]
                tokens = [str(ORDINAL_MAP[lemma_lower])]
                pos = ['CD']
                ner = ['ORDINAL']
                break
            if lemma_lower == 'quarter' and i > 0 and sig.pos_tags[i - 1] == 'CD':
                span = [i - 1, i]
                tokens = [sig.tokens[i - 1]]
                pos = [sig.pos_tags[i - 1]]
                ner = [sig.ner_tags[i - 1]]
                break
        else:
            break
        sig.replace_span(span, tokens, pos, ner)


def join_model_name(sig):
    # Joint the words starting with a cap letter which is followed by '^-\d+$'
    while True:
        span = None
        if len(sig.tokens) < 2:
            break
        for i in range(len(sig.tokens) - 1):
            x, y = sig.tokens[i: i + 2]
            if x.isalpha() and x.isupper() and re.search(r'^-\d+$', y):
                span = list(range(i, i + 2))
                joined_tokens = ''.join([x, y])
                if joined_tokens in ('K-12'):
                    continue
                break
        else:
            break
        sig.replace_span(span, [joined_tokens], ['NNP'], ['ENTITY'])


def join_time_description(sig):
    # 4 o'clock; 4 am; 4 a.m., etc.
    while True:
        span = None
        if len(sig.tokens) < 2:
            break
        for i in range(1, len(sig.tokens)):
            x, y = sig.tokens[i - 1: i + 1]
            if y.lower() in ("o'clock", 'am', 'a.m.', 'pm', 'p.m') and re.search(r'^\d+[.:]?\d*[.:]?\d*$', x):
                span = list(range(i - 1, i + 1))
                joined_tokens = ''.join([x, y])
                pos = 'CD'
                ner = 'TIME'
                break
            if y.lower() in ("o'clock", 'am', 'a.m.', 'pm', 'p.m') and x.isalpha():
                try:
                    x = w2n.word_to_num(x)
                except:
                    continue
                x = str(x)
                span = list(range(i - 1, i + 1))
                joined_tokens = ''.join([x, y])
                pos = 'CD'
                ner = 'TIME'
                break
            if y == 'Greenwich' and i + 2 < len(sig.tokens) and sig.tokens[i + 1: i + 3] == ['Mean', 'Time']:
                span = list(range(i, i + 3))
                joined_tokens = 'GMT'
                pos = 'NNP'
                ner = 'TIME'
                break
            if y in ('century', 'Century'):
                m = re.search(r'^(\d+)(st|nd|rd|th)?$', x)
                if m and m.group(1) != '':
                    span = list(range(i - 1, i + 1))
                    joined_tokens = ''.join([m.group(1), y.lower()])
                    pos = 'CD'
                    ner = 'TIME'
                    break
                elif x == 'first' and sig.tokens[i - 2] == '-' and sig.tokens[i - 3] == 'twenty':
                    span = list(range(i - 3, i + 1))
                    joined_tokens = '21century'
                    pos = 'CD'
                    ner = 'TIME'
                    break
                elif x.lower() == 'eighth':
                    span = list(range(i - 1, i + 1))
                    joined_tokens = '8century'
                    pos = 'CD'
                    ner = 'TIME'
                    break
                elif x.lower() == 'fifth':
                    span = list(range(i - 1, i + 1))
                    joined_tokens = '5century'
                    pos = 'CD'
                    ner = 'TIME'
                    break
                else:
                    try:
                        x = w2n.word_to_num(x)
                    except:
                        continue
                    span = list(range(i - 1, i + 1))
                    joined_tokens = ''.join([x, y.lower()])
                    pos = 'CD'
                    ner = 'TIME'
                    break
        else:
            break
        sig.replace_span(span, [joined_tokens], [pos], [ner])


def split_entity_with_slash(sig):
    # Split named entity word with '/', e.g. 'Romney/McDonnell'.
    while True:
        index = None
        for i, token in enumerate(sig.tokens):
            if (len(token) and token[0].isupper() and '/' in token and
                token.index('/') + 1 < len(token) and
                token[token.index('/') + 1].isupper()
            ):
                index = i
                break
        else:
            break
        pos = sig.pos_tags[index]
        ner = sig.ner_tags[index]
        x, y = sig.tokens[index].split('/', 1)
        sig.replace_span([index], [x, '/', y], [pos, 'SYM', pos], [ner, ner, ner])


def split_entity_with_non(sig):
    # Split named entity word with 'non', e.g. 'nonRomney'.
    while True:
        index = None
        for i, token in enumerate(sig.tokens):
            if token.startswith('non') and len(token) > 3 and token[3].isupper():
                index = i
                break
        else:
            break
        pos = sig.pos_tags[index]
        ner = sig.ner_tags[index]
        x = sig.tokens[index]
        sig.replace_span([index], ['non', x[3:]], ['JJ', pos], ['O', ner])


def split_entity_prefix(sig, prefix):
    # Split word with 'anti-' prefix.
    while True:
        index = None
        for i, lemma in enumerate(sig.lemmas):
            if lemma.lower().startswith(prefix + '-'):
                index = i
                break
        else:
            break
        pos = sig.pos_tags[index]
        ner = sig.ner_tags[index]
        _, lemma = sig.lemmas[index].split('-', 1)
        if lemma == '':
            sig.replace_span([index], [prefix], ['JJ'], ['O'])
        else:
            sig.replace_span([index], [prefix, lemma], ['JJ', pos], [ner, ner])


def split_unit_with_number(sig):
    # Split unit with number, e.g. '30pence'.
    while True:
        index = None
        for i, lemma in enumerate(sig.lemmas):
            if re.search(r'^\d+(ps|pence)$', lemma):
                index = i
                break
        else:
            break
        lemma = sig.lemmas[index]
        x = re.split(r'(ps|pence)$', lemma)[0]
        y = lemma[len(x):]
        sig.replace_span([index], [x, y], ['CD', 'NN'], ['NUMBER', 'O'])


def split_ratio(sig):
    # Split ratio with number, e.g. '1:1.4'.
    while True:
        index = None
        for i, lemma in enumerate(sig.lemmas):
            if '.' in lemma and re.search(r'^\d+\.?\d*:\d+\.?\d*$', lemma):
                index = i
                break
        else:
            break
        lemma = sig.lemmas[index]
        x, y = lemma.split(':')
        sig.replace_span([index], [x, ':', y], ['CD', ':', 'CD'], ['NUMBER', 'O', 'NUMBER'])


def split_number_with_dash_prefix(sig):
    # Split number with dash prefix, e.g. '-6'
    while True:
        index = None
        for i, lemma in enumerate(sig.lemmas):
            if re.search(r'^-\d+$', lemma):
                index = i
                break
        else:
            break
        lemma = sig.lemmas[index]
        ner_tag = sig.ner_tags[index]
        if ner_tag in ('0', 'O'):
            ner_tag = 'NUMBER'
        x = lemma[0]
        y = lemma[1:]
        sig.replace_span([index], [x, y], [':', 'CD'], ['O', ner_tag])


def split_date_duration(sig):
    # 201005-201006
    while True:
        index = None
        x = None
        for i, lemma in enumerate(sig.lemmas):
            if re.search(r'^-\d{8}$', lemma) or re.search(r'^-\d{6}$', lemma):
                index = i
                _, x = lemma.split('-')
                break
        else:
            break
        sig.replace_span([index], [x], ['CD'], ['DATE'])



def split_numerical_date(sig):
    # Split the numerical date, e.g. 20080710.
    while True:
        index = None
        year, month, day = None, None, None
        for i, lemma in enumerate(sig.lemmas):
            if (re.search(r'^\d{8}$', lemma) and
                1000 < int(lemma[:4]) < 2100 and  # year
                0 < int(lemma[4:6]) < 13 and  # month
                0 < int(lemma[6:]) < 32  # day
            ):
                index = i
                year, month, day = int(lemma[:4]), int(lemma[4:6]), int(lemma[6:])
                month = '{:02d}'.format(month)
                day = '{:02d}'.format(day)
                break
            elif (re.search(r'^\d{5}$', lemma) and
                    0 < int(lemma[1:3]) < 13 and  # month
                    0 < int(lemma[3:]) < 32  # day
            ):
                index = i
                year, month, day = '0' + lemma[0], int(lemma[1:3]), int(lemma[3:])
                month = '{:02d}'.format(month)
                day = '{:02d}'.format(day)
                break
            elif (re.search(r'^\d{6}$', lemma) and
                    0 < int(lemma[2:4]) < 13 and  # month
                    0 <= int(lemma[4:]) < 32  # day
            ):
                index = i
                year = int(lemma[:2])
                month, day = int(lemma[2:4]), int(lemma[4:])
                year = '{:02d}'.format(year)
                month = '{:02d}'.format(month)
                day = '{:02d}'.format(day)
                break
            elif re.search(r'^\d+/\d+/\d+$', lemma):
                index = i
                year, month, day = lemma.split('/')
                break
            elif re.search(r'^\d+-/\d+-/\d+$', lemma):
                index = i
                year, month, day = lemma.split('-')
                break
        else:
            break
        pos = 'CD'
        ner = 'DATE'
        sig.replace_span([index], [str(year), str(month), str(day)], [pos] * 3, [ner] * 3)


def split_year_month(sig):
    while True:
        index = None
        year, month = None, None
        for i, token in enumerate(sig.tokens):
            m = re.search(r'^(\d+)/(\d+)-*$', token)
            if m:
                index = i
                year, month = m.group(1), m.group(2)
                break
            m = re.search(r'^(\d{4})(\d{2})00$', token)
            if m:
                index = i
                year, month = m.group(1), m.group(2)
                break
        else:
            break
        sig.replace_span([index], [year, month], ['CD', 'CD'], ['DATE', 'DATE'])


def split_era(sig):
    while True:
        index = None
        year, era = None, None
        for i, token in enumerate(sig.tokens):
            if re.search(r'^\d{4}BC$', token):
                index = i
                year, era = token[:4], token[4:]
                break
        else:
            break
        sig.replace_span([index], [year, era], ['CD', 'NN'], ['DATE', 'DATE'])


def split_911(sig):
    while True:
        index = None
        for i, token in enumerate(sig.tokens):
            if token == '911':
                index = i
                break
        else:
            break
        sig.replace_span([index], ['09', '11'], ['CD', 'CD'], ['DATE', 'DATE'])


def replace_NT_dollar_abbr(sig):
    # Replace 'NT' in front of '$' with 'Taiwan'.
    for i, token in enumerate(sig.tokens):
        if token == 'NT' and len(sig.tokens) > i + 1 and sig.tokens[i + 1] in ('$', 'dollars', 'dollar'):
            sig.replace_span([i], ['Taiwan'], ['NNP'], ['COUNTRY'])


if __name__ == '__main__':
    import argparse
    from stog.data.dataset_readers.sig_parsing.io import SIGIO

    parser = argparse.ArgumentParser('input_cleaner.py')
    parser.add_argument('--sig_files', nargs='+', default=[])

    args = parser.parse_args()

    for file_path in args.sig_files:
        with open(file_path + '.input_clean', 'w', encoding='utf-8') as f:
            for sig in SIGIO.read(file_path):
                clean(sig)
                f.write(str(sig) + '\n\n')

