#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
"""

import kneser_ney
from typing import Callable, Sequence, Iterator
from math import exp

Token = str

def main():
    n = 3
    with open('sense.txt', encoding='UTF-8') as corpus_file:
        corpus = corpus_file.read()
    sense_grams = ngrams(corpus.split(), n=n)
    lm = kneser_ney.KneserNeyLM(n, sense_grams, end_pad_symbol='<start>')

    score = lm.score_sent(('This', 'is', 'a'))
    print(f"{exp(score)} ({score})")


def ngrams(tokens: Sequence[Token], n: int=3) -> Iterator[Sequence[Token]]:
    context = n - 1
    padding_token = '<start>'

    # Generate a sentence for each element in the vector.
    for i, element in enumerate(tokens):
        # Ensure the beginning of the slice is AT LEAST 0 (or else the slice
        # will start from THE END of the vector!)
        beginning = at_least(0, i - context)
        real_context = tokens[beginning:i]
        # Need to add padding when i is less than the context size.
        if i < context:
            padding = (padding_token,) * (context - i)
            yield padding + tuple(real_context) + (element,)
        else:
            # All tokens come from the vector
            yield tuple(real_context) + (element,)


def at_least(m: int, n: int) -> int:
    return max(m, n)


def at_most(m: int, n: int) -> int:
    return min(m, n)


def test_ngrams():
    assert list(ngrams("I'm a little teapot".split(), n=3)) == [
        ('<start>', '<start>', "I'm"),
        ('<start>', "I'm", 'a'),
        ("I'm", 'a', 'little'),
        ('a', 'little', 'teapot')
    ]


if __name__ == '__main__':
    main()
