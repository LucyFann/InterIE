import re
    

match_of = re.compile(":[0-9a-zA-Z]*-of")
match_no_of = re.compile(":[0-9a-zA-Z]*(?!-of)")

def readFile(filepath):
    with open(filepath, 'r') as content_file:
        content = content_file.read()
    sig_t = content
    sig_t = re.sub(match_no_of,":label",sig_t)
    sig_t = re.sub(match_of,":label-of",sig_t)
    print (sig_t)

import sys
readFile(sys.argv[1])
