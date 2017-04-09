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


import sys
import csv

import numpy as np  # type: ignore
#from sklearn.cluster import KMeans  # type: ignore
import jenkspy  # type: ignore

from operator import attrgetter
from typing import NamedTuple, List, Tuple
from math import log, exp


class BaseSourceFile(NamedTuple):
    filehash: str
    ntokens: int
    sloc: int
    minified: bool
    path: str


class SourceFile(BaseSourceFile):
    @property
    def ratio(self):
        return self.ntokens / self.sloc



def to_bool(text: str) -> bool:
    if text == 'True':
        return True
    elif text == 'False':
        return False
    else:
        raise ValueError(text)


def dump(breakpoint: float, files: List[SourceFile]) -> None:
    for sf in files:
        label = 'gen' if sf.ratio > breakpoint else 'hw'
        print(f"{label}:{sf.ratio:.1f}:{sf.filehash}")


if __name__ == '__main__':
    files = []
    with open('tokens.csv') as csvfile:
        # filehash ntokens sloc min.js path
        reader = csv.DictReader(csvfile)
        for row in reader:
            files.append(SourceFile(
                filehash=row['filehash'],
                ntokens=int(row['ntokens']),
                sloc=int(row['sloc']),
                minified=to_bool(row['min.js']),
                path=row['path']
            ))

    # Sort by ratio, ascending.
    files.sort(key=attrgetter('ratio'))

    # Prepare the data for jenks natural break algorithm
    xs = np.zeros((len(files), 1), np.float64)
    for i, source in enumerate(files):
        xs[i] = log(source.ratio)

    log_break_point, = jenkspy.jenks_breaks(xs, nb_class=2)
    break_point = exp(log_break_point)

    print(f'# {break_point:.1f}')
    dump(break_point, files)
