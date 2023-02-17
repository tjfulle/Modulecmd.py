# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright © 2015-2016 Franklin "Snaipe" Mathieu <http://snai.pe/>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import re

_ANSI_CODE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

def word_size(word):
  return len(_ANSI_CODE.sub('', word))

def wrap(text, width=80, subsequent_indent=''):
  words = text.split()
  line_size = 0
  lines = [[]]

  for w in words:
    size = word_size(w) + 1
    if size == 0:
      continue
    if line_size + size - 1 > width and line_size > width / 2:
      line_size = len(subsequent_indent)
      lines.append([])
    while line_size + size - 1 > width:
      stripped = width - line_size - 1
      lines[-1].append(w[:stripped] + '-')
      line_size = len(subsequent_indent)
      lines.append([])
      w = w[stripped:]
      size -= stripped
    if size == 0:
      continue
    lines[-1].append(w)
    line_size += size
  return [subsequent_indent + ' '.join(words) for words in lines]

