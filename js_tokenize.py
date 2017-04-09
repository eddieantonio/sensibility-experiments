#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import atexit
import json
import os
import signal
import socket
import struct
import tempfile

from pathlib import Path

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
        value = self._communicate('?', contents.encode('UTF-8'))
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            assert False, f"Unknown value: {value!r}"

    def tokenize(self, contents: str) -> str:
        ...

    def close(self) -> None:
        self.quit()
        self.server_address.unlink()

    def _communicate(self, code: str, payload: bytes) -> str:
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
        msg = sock.recv(4096)
        sock.close()
        return msg.decode('utf-8')

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

if __name__ == '__main__':
    try:
        while True:
            code = input('> ')
            print(check_syntax(code))
    except EOFError:
        pass
