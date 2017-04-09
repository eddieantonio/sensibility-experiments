#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sqlite3
import sys
from pprint import pprint

from js_tokenize import tokenize

conn = sqlite3.connect('sources.sqlite3')
cur = conn.execute('''
    SELECT owner, repo, path, source FROM source_file
    where hash = ?
''', (sys.argv[1],))


owner, repo, path, source = cur.fetchone()
tokens = tokenize(source)
pprint(tokens)
#print(f"/* {owner}/{repo}: {path}: {len(tokens)} tokens */")
#print(source.decode('utf8'))
