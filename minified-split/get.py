#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2017 Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
print(f"/* {owner}/{repo}: {path}: {len(tokens)} tokens */")
print(source.decode('utf8'))
#pprint(tokens)
