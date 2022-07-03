import re

match_of = re.compile(":[0-9a-zA-Z]*-of")
match_no_of = re.compile(":[0-9a-zA-Z]*(?!-of)")

placeholder = '<`_placeholder_`>'


def readFile(filepath, keeplabel):
    with open(filepath, 'r') as content_file:
        content = content_file.read()
    sig_t = content
    assert placeholder not in sig_t, 'conflicting placeholder'
    sig_t = sig_t.replace(keeplabel + ' ', placeholder)
    sig_t = re.sub(match_no_of, ":label", sig_t)
    sig_t = re.sub(match_of, ":label-of", sig_t)
    sig_t = sig_t.replace(placeholder, keeplabel + ' ')
    print(sig_t)


import sys

readFile(sys.argv[1], sys.argv[2])
