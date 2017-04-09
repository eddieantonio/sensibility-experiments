#!/usr/bin/env node
/*
 * Copyright 2016 Eddie Antonio Santos <easantos@ualberta.ca>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const net = require('net');
const esprima = require('esprima');
const assert = require('assert');

const HEADER_LENGTH = 1 + 4;

if (require.main === module) {
  const socketPath = process.argv[2];
  assert(socketPath.match(/[.]sock$/));

  const server = net.createServer(client => {
    let buffer = null;
    let receivedLength = 0;
    let expectedLength = null;
    let command = null;

    /* Parse each packet. */
    client.on('data', chunk => {
      //  Message ::= Type Length Payload
      //  Type    ::= '?' | 'T' | 'Q'
      //  Length  ::= 32-bit big-endian integer
      //  Payload ::= length * uint8
      if (!buffer) {
        // New message! Parse its header.
        assert(chunk.length >= HEADER_LENGTH);
        const code = chunk.toString('ascii', 0, 1);

        /* Regardless of the payload size, expect 0 bytes. */
        if (code == 'X') {
          expectedLength = 0;
        } else {
          expectedLength = chunk.readUInt32BE(1);
        }

        /* TODO: probably have some maximum size. */
        buffer = Buffer.alloc(expectedLength);
        command = {
          'T'() {
            const source = buffer.toString('utf8');
            return tokenize(source);
          },
          '?'() {
            const source = buffer.toString('utf8');
            return checkSyntax(source);
          },
          'Q'() {
            return true;
          }
        }[code];
        assert(command !== undefined);

        appendChunk(HEADER_LENGTH);
      } else {
        appendChunk();
      }

      /* Append a chunk. */
      function appendChunk(offset = 0) {
        const length = chunk.length - offset;
        assert(length + receivedLength <= expectedLength);
        chunk.copy(buffer, 0, offset);
        receivedLength += length;

        if (receivedLength >= expectedLength) {
          console.log(`${receivedLength}/${expectedLength}`);
          try {
            const output = command();
            console.log('Computed');
            finalize(output);
          } catch (e) {
            finalize(e);
          }
        }
      }
    });

    function finalize(source) {
      const response = Buffer.from(JSON.stringify(source));
      const length = response.length;
      const header = Buffer.alloc(4);
      header.writeUInt32BE(length, 0);
      const payload = Buffer.concat([header, response], 4 + length);

      client.write(payload, () => {
        console.log('Wrote all datums.');
      });
    }

    client.on('error', (err) => {
      console.log(err);
    });

    client.on('close', (hadError) => {
      console.log(`Close. Had error? ${hadError}`);
    });
  });

  server.listen(socketPath);
}

function tokenize(source) {
  source = removeShebangLine(source);

  /* TODO: retry on illegal tokens. */

  const sourceType = deduceSourceType(source);
  const tokens = esprima.tokenize(source, {
    sourceType,
    loc: true,
    tolerant: true
  });

  return tokens;
}

function checkSyntax(source) {
  source = removeShebangLine(source);
  const sourceType = deduceSourceType(source);

  try {
    esprima.parse(source, { sourceType });
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Remove the shebang line, if there is one.
 */
function removeShebangLine(source) {
  return source.replace(/^#![^\r\n]+/, '');
}


/*
  Adapted from: http://esprima.org/demo/parse.js

  Copyright (C) 2013 Ariya Hidayat <ariya.hidayat@gmail.com>
  Copyright (C) 2012 Ariya Hidayat <ariya.hidayat@gmail.com>
  Copyright (C) 2011 Ariya Hidayat <ariya.hidayat@gmail.com>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  */
function deduceSourceType(code) {
  try {
    esprima.parse(code, { sourceType: 'script' });
    return 'script';
  } catch (e) {
    return 'module';
  }
}

/* eslint no-console: 0 */
