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


import atexit
import json
import os
import signal
import socket
import struct
import tempfile
import time

from pathlib import Path
from typing import Any, List, Sequence, Union, cast

from sensibility import Token  # type: ignore

THIS_DIRECTORY = Path(__file__).parent
TOKENIZE_JS_BIN = THIS_DIRECTORY / 'tokenize-js' / 'wrapper.sh'

POLITE = False


class Server:
    def __init__(self, name: Path) -> None:
        self.server_address = name
        self._ready = False

    def connect(self) -> 'Server':
        assert not self.server_address.exists()
        self._pid = self._spawn()
        return self

    def quit(self) -> None:
        if POLITE:
            self._communicate(b'Q', b'')
        os.kill(self._pid, signal.SIGTERM)

    def check_syntax(self, contents: Union[str, bytes]) -> bool:
        return self._communicate(b'?', to_buffer(contents))

    def tokenize(self, contents: str) -> Sequence[Token]:
        value = self._communicate(b'T', to_buffer(contents))
        if isinstance(value, list):
            return [Token.from_json(t) for t in value]
        raise Exception(f"Bad return: {value!r}")

    def close(self) -> None:
        self.quit()
        self.server_address.unlink()

    def _communicate(self, code: bytes, payload: bytes) -> Any:
        self._wait_until_ready()
        # Establish a new socket.
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(self.server_address))
        sock.sendall(b''.join((
            code,
            struct.pack('>1I', len(payload)),
            payload
        )))
        msg = self._slurp(sock)
        sock.close()
        return json.loads(msg)

    def _wait_until_ready(self):
        if self._ready:
            return
        delta = 10  # ms
        max_sleep = 60_000  # ms

        sleep_time = 0
        while sleep_time < max_sleep:
            time.sleep(delta / 1000)
            if self.server_address.exists():
                break
        else:
            raise Exception(f"Waited maximum amount of time: {max_sleep}")
        self._ready = True

    def _slurp(self, sock: socket.socket) -> bytes:
        # Wait for the first few messages
        sock.settimeout(30)
        header = sock.recv(4)
        payload_size: int = struct.unpack('>I', header)[0]
        bytes_left = payload_size
        sock.setblocking(True)
        chunks: List[bytes] = []
        while bytes_left > 0:
            chunk = sock.recv(bytes_left)
            if len(chunk) == 0:
                break
            chunks.append(chunk)
            bytes_left -= len(chunk)
        payload = b''.join(chunks)
        assert len(payload) == payload_size
        return payload

    def _spawn(self) -> int:
        pid = os.fork()
        if pid == 0:
            # child
            os.execl(str(TOKENIZE_JS_BIN),
                     str(TOKENIZE_JS_BIN),
                     str(self.server_address))
        return pid


def to_buffer(contents: Union[str, bytes]) -> bytes:
    if isinstance(contents, bytes):
        return contents
    else:
        return contents.encode('UTF-8')


_server = Server(Path('/tmp') / f"tokenize-{os.getpid()}.sock")
_server.connect()
atexit.register(_server.close)

check_syntax = _server.check_syntax
tokenize = _server.tokenize

if __name__ == '__main__':
    try:
        while True:
            code = input('> ')
            print(tokenize(code))
    except EOFError:
        pass
