from typing import List, Tuple, Type, Union

import asyncio
import os
import tempfile
import time
import uuid

import zmq
import zmq.asyncio as zmqa
from termcolor import colored


from ..utils import helper
from . import zmq_ops


class BaseZMQService():
    def __init__(self, args):
        self.args = args
        self.logger = helper.set_logger(self.__class__.__name__, args.verbose)
        self.ctrl_with_ipc = (os.name != 'nt') and self.args.ctrl_with_ipc
        if self.ctrl_with_ipc:
            self.ctrl_addr = zmq_ops.get_random_ipc()
        else:
            self.ctrl_addr = 'tcp://%s:%d' % ('127.0.0.1', self.args.port_ctrl)

    def start(self):
        async_loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(async_loop)

        async_ctx = zmqa.Context().instance()

        self.in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue()

        self.in_sock, _ = zmq_ops.build_socket(
            async_loop, async_ctx, self.args.host_in, self.args.port_in, self.args.socket_in)
        self.logger.info('input %s:%s' % (self.args.host_in,
                                          colored(self.args.port_in, 'yellow')))

        self.out_sock, _ = zmq_ops.build_socket(
            async_loop, async_ctx, self.args.host_out, self.args.port_out, self.args.socket_out)
        self.logger.info('output %s:%s' % (self.args.host_out,
                                           colored(self.args.port_out, 'yellow')))

        async_loop.create_task(self.receive_messages())
        async_loop.create_task(self.consume_messages())
        async_loop.create_task(self.sendout_messages())

        async_loop.run_forever()
        async_loop.close()
        # s.close()

    async def consume_messages(self):
        while True:
            value = await self.in_queue.get()
            print(value)
            await self.out_queue.put(value)

    async def receive_messages(self):
        while True:
            msg = await self.in_sock.recv()
            print(f"recv {msg}")
            await self.in_queue.put(msg)

    async def sendout_messages(self):
        while True:
            msg = await self.out_queue.get()
            await self.out_sock.send(msg)
            print(f"sent {msg}")
