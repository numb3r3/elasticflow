import os
import tempfile
import uuid

import zmq
import zmq.asyncio

from enum import Enum


class BetterEnum(Enum):
    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s):
        try:
            return cls[s]
        except KeyError:
            raise ValueError('%s is not a valid enum for %s' % (s, cls))


def get_random_ipc() -> str:
    try:
        tmp = os.environ['GNES_IPC_SOCK_TMP']
        if not os.path.exists(tmp):
            raise ValueError(
                'This directory for sockets ({}) does not seems to exist.'.format(tmp))
        tmp = os.path.join(tmp, str(uuid.uuid1())[:8])
    except KeyError:
        tmp = tempfile.NamedTemporaryFile().name
    return 'ipc://%s' % tmp


class SocketType(BetterEnum):
    PULL_BIND = 0
    PULL_CONNECT = 1
    PUSH_BIND = 2
    PUSH_CONNECT = 3
    SUB_BIND = 4
    SUB_CONNECT = 5
    PUB_BIND = 6
    PUB_CONNECT = 7
    PAIR_BIND = 8
    PAIR_CONNECT = 9

    @property
    def is_bind(self):
        return self.value % 2 == 0

    @property
    def paired(self):
        return {
            SocketType.PULL_BIND: SocketType.PUSH_CONNECT,
            SocketType.PULL_CONNECT: SocketType.PUSH_BIND,
            SocketType.SUB_BIND: SocketType.PUB_CONNECT,
            SocketType.SUB_CONNECT: SocketType.PUB_BIND,
            SocketType.PAIR_BIND: SocketType.PAIR_CONNECT,
            SocketType.PUSH_CONNECT: SocketType.PULL_BIND,
            SocketType.PUSH_BIND: SocketType.PULL_CONNECT,
            SocketType.PUB_CONNECT: SocketType.SUB_BIND,
            SocketType.PUB_BIND: SocketType.SUB_CONNECT,
            SocketType.PAIR_CONNECT: SocketType.PAIR_BIND
        }[self]


def build_socket(io_loop, ctx: 'zmq.asyncio.Context', host: str, port: int,
                 socket_type: 'SocketType', use_ipc: bool = False) -> Tuple['zmq.Socket', str]:
    sock = {
        SocketType.PULL_BIND: lambda: ctx.socket(zmq.PULL, io_loop=io_loop),
        SocketType.PULL_CONNECT: lambda: ctx.socket(zmq.PULL, io_loop=io_loop),
        SocketType.SUB_BIND: lambda: ctx.socket(zmq.SUB, io_loop=io_loop),
        SocketType.SUB_CONNECT: lambda: ctx.socket(zmq.SUB, io_loop=io_loop),
        SocketType.PUB_BIND: lambda: ctx.socket(zmq.PUB, io_loop=io_loop),
        SocketType.PUB_CONNECT: lambda: ctx.socket(zmq.PUB, io_loop=io_loop),
        SocketType.PUSH_BIND: lambda: ctx.socket(zmq.PUSH, io_loop=io_loop),
        SocketType.PUSH_CONNECT: lambda: ctx.socket(zmq.PUSH, io_loop=io_loop),
        SocketType.PAIR_BIND: lambda: ctx.socket(zmq.PAIR, io_loop=io_loop),
        SocketType.PAIR_CONNECT: lambda: ctx.socket(zmq.PAIR, io_loop=io_loop)
    }[socket_type]()
    sock.setsockopt(zmq.LINGER, 0)

    if socket_type.is_bind:
        if use_ipc:
            sock.bind(host)
        else:
            sock.bind('tcp://%s:%d' % (host, port))
    else:
        if port is None:
            sock.connect(host)
        else:
            sock.connect('tcp://%s:%d' % (host, port))

    # Note: the following very dangerous for pub-sub socketc
    sock.setsockopt(zmq.RCVHWM, 10)
    # limit of network buffer 100M
    sock.setsockopt(zmq.RCVBUF, 10 * 1024 * 1024)

    sock.setsockopt(zmq.SNDHWM, 10)
    # limit of network buffer 100M
    sock.setsockopt(zmq.SNDBUF, 10 * 1024 * 1024)

    return sock, sock.getsockopt_string(zmq.LAST_ENDPOINT)
