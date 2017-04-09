#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import atexit
import json
import os
import signal
import socket
import struct
import tempfile
import logging

from pathlib import Path
from typing import Any, Sequence

from sensibility import Token  # type: ignore

THIS_DIRECTORY = Path(__file__).parent
TOKENIZE_JS_BIN = THIS_DIRECTORY / 'tokenize-js' / 'wrapper.sh'


class Server:
    def __init__(self, name: Path) -> None:
        self.server_address = name

    def connect(self) -> 'Server':
        assert not self.server_address.exists()
        self._pid = self._spawn()
        return self

    def quit(self) -> None:
        self._communicate('Q', b'')
        os.kill(self._pid, signal.SIGTERM)

    def check_syntax(self, contents: str) -> bool:
        return self._communicate('?', contents.encode('UTF-8'))

    def tokenize(self, contents: str) -> Sequence[Token]:
        value = self._communicate('T', contents.encode('UTF-8'))
        if isinstance(value, list):
            return [Token.from_json(t) for t in value]
        raise Exception(f"Bad return: {value!r}")

    def close(self) -> None:
        self.quit()
        self.server_address.unlink()

    def _communicate(self, code: str, payload: bytes) -> Any:
        # Establish a new socket.
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(self.server_address))
        parts = [
            code.encode('ascii'),
            struct.pack('>1I', len(payload)),
            payload
        ]
        for part in parts:
            sock.send(part)
        msg = self._slurp(sock)
        sock.close()
        return json.loads(msg.decode('UTF-8'))

    def _slurp(self, sock: socket.socket) -> bytes:
        # Wait for the first few messages
        sock.settimeout(30)
        chunks = [sock.recv(128)]
        logging.debug(f'initial read: {len(chunks[0])}')
        sock.setblocking(False)
        while True:
            try:
                chunk = sock.recv(4096)
            except BlockingIOError:
                break
            logging.debug(f'subsequent read: {len(chunk)}')
            if len(chunk) == 0:
                break
            chunks.append(chunk)

        buf = b''.join(chunks)
        logging.debug(f'read {len(buf)} bytes total')
        return buf

    def _spawn(self) -> int:
        pid = os.fork()
        if pid == 0:
            # child
            os.execl(str(TOKENIZE_JS_BIN),
                     str(TOKENIZE_JS_BIN),
                     str(self.server_address))
        return pid


_server = Server(Path('/tmp') / f"tokenize-{os.getpid()}.sock")
_server.connect()
atexit.register(_server.close)

check_syntax = _server.check_syntax
tokenize = _server.tokenize

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        while True:
            code = input('> ')
            print(tokenize(code))
    except EOFError:
        pass
