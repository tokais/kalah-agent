# KALAH GAME PROTOCOL LIBRARY                    -*- mode: python; -*-

# Copyright 2021, 2022, 2023, Philip Kaludercic

# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above  copyright notice  and this  permission notice  appear in  all
# copies.

# THE  SOFTWARE IS  PROVIDED  "AS  IS" AND  THE  AUTHOR DISCLAIMS  ALL
# WARRANTIES  WITH  REGARD  TO  THIS SOFTWARE  INCLUDING  ALL  IMPLIED
# WARRANTIES OF  MERCHANTABILITY AND  FITNESS. IN  NO EVENT  SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY  DAMAGES WHATSOEVER RESULTING FROM LOSS  OF USE, DATA
# OR PROFITS,  WHETHER IN AN  ACTION OF CONTRACT, NEGLIGENCE  OR OTHER
# TORTIOUS ACTION,  ARISING OUT OF  OR IN  CONNECTION WITH THE  USE OR
# PERFORMANCE OF THIS SOFTWARE.

import inspect
import re
import os
import sys
import socket
import threading
from threading import Thread, Event
import multiprocessing as mp
import copy
import time

try:
    import websocket
except ModuleNotFoundError:
    pass


_BOARD_PATTERN = re.compile(r'^(<(\d+(?:,\d+){4,})>)\s*')


NORTH = True
SOUTH = not NORTH


class Board:
    """Board state representation."""

    @staticmethod
    def parse(raw):
        """Turn a KGP board representation into a board object."""
        match = _BOARD_PATTERN.match(raw)
        assert match

        try:
            data = [int(d) for d in match.group(2).split(',')]
            size, south, north, *rest = data
            if len(data) != data[0] * 2 + 2 + 1:
                return None

            return Board(south, north, rest[:size], rest[size:])
        except ValueError:
            return None

    def __init__(self, south, north, south_pits, north_pits):
        """Create a new board."""
        assert len(north_pits) == len(south_pits)

        self.north = north
        self.south = south
        self.north_pits = north_pits
        self.south_pits = south_pits
        self.size = len(north_pits)

    def __eq__(self, other):
        """True if the same board as OTHER."""
        return (self.north == other.north and
                self.south == other.south and
                self.north_pits == other.north_pits and
                self.south_pits == other.south_pits)

    def __str__(self):
        """Return board in KGP board representation."""
        data = [self.size,
                self.south,
                self.north,
                *self.south_pits,
                *self.north_pits]

    
        n = self.size
        south_kalah = self.south
        north_kalah = self.north
        south_pits = self.south_pits
        north_pits = self.north_pits

        # Build the ASCII representation
        board_width = len(str(max(max(north_pits), max(south_pits))))  # Width of the widest number for formatting
        fmt = f"{{:^{board_width}}}"  # Centered formatting template for numbers

        # North pits row
        north_pits_row = " ".join(fmt.format(stones) for stones in reversed(north_pits))

        # South pits row
        south_pits_row = " ".join(fmt.format(stones) for stones in south_pits)

        # North kalah, pits, and South kalah combined
        north_row = f"{north_kalah} | {north_pits_row} |"
        south_row = f"| {south_pits_row} | {fmt.format(south_kalah)}"
        return f"{north_row}\n{" "*(len(str(north_kalah))+1)}{south_row}\n"

    def __getitem__(self, key):
        """
        Convenience assessor for stores and pits.

        If key is NORTH or SOUTH, return the number of stones in the
        respective pits.

        If key is a part of either NORTH or SOUTH and a 0-indexed pit,
        call the method pit.
        """
        if key == NORTH:
            return self.north
        elif key == SOUTH:
            return self.south
        side, pit = key
        return self.pit(side, pit)

    def __setitem__(self, key, value):
        """
        Convenience modifier for stores and pits.

        If key is NORTH or SOUTH, set the number of stones in the
        respective pits.

        If key is a part of either NORTH or SOUTH and a 0-indexed pit,
        set the stone count for the pit.
        """
        if key == NORTH:
            self.north = value
        elif key == SOUTH:
            self.south = value
        else:
            side, pit = key
            self.side(side)[pit] = value

    def side(self, side):
        """Return the pits for SIDE."""
        assert side in (NORTH, SOUTH)

        if side == NORTH:
            return self.north_pits
        elif side == SOUTH:
            return self.south_pits

    def pit(self, side, pit):
        """Return number of seeds in PIT on SIDE."""
        assert 0 <= pit < self.size
        return self.side(side)[pit]

    def is_legal(self, side, move):
        """Check if side can make move."""
        return self.pit(side, move) > 0

    def legal_moves(self, side):
        """Return a list of legal moves for side."""
        return [move for move in range(self.size)
                if self.is_legal(side, move)]

    def is_final(self):
        return (not self.legal_moves(NORTH)) or (not self.legal_moves(SOUTH))

    def copy(self):
        """Return a deep copy of the current board state."""
        return copy.deepcopy(self)

    def _collect(self):
        self.north += sum(self.north_pits)
        self.north_pits = [0] * len(self.north_pits)
        self.south += sum(self.south_pits)
        self.south_pits = [0] * len(self.south_pits)

        return self, False

    def sow(self, side, pit, pure=True):
        """
        Sow the stones from pit on side.

        By default, sow returns a new board object and a boolean to
        indicate a repeat move. To change the state of this object set
        the key pure to False.
        """
        b = self
        if pure:
            b = self.copy()

        assert b.is_legal(side, pit)

        me = side
        pos = pit + 1
        stones = b[side, pit]
        b[side, pit] = 0

        while stones > 0:
            if pos == self.size:
                if side == me:
                    b[me] += 1
                    stones -= 1
                side = not side
                pos = 0
            else:
                b[side, pos] += 1
                pos += 1
                stones -= 1

        if pos == 0 and not me == side:
            if b.is_final():
                return b._collect()
            return b, True
        elif side == me and pos > 0:
            last = pos - 1
            other = self.size - 1 - last
            if b[side, last] == 1 and b[not side, other] > 0:
                b[side] += b[not side, other] + 1
                b[not side, other] = 0
                b[side, last] = 0

        if b.is_final():
            b._collect()

        return b, False


def connect(agent, host='wss://kalah.kwarc.info/socket', port=2671, token=None, name=None, authors=[], debug=False):
    """
    Connect to KGP server at host:port as agent.

    Agent is a generator function, that produces as many moves as it
    can until the server ends a search request.

    The optional arguments TOKEN, NAME and AUTHORS are used to send
    the server optional information about the client implementation.

    If DEBUG has a true value, the network communication is printed on
    to the standard error stream.
    """
    assert inspect.isgeneratorfunction(agent)

    COMMAND_PATTERN = re.compile(r"""
^                   # beginning of line
\s*                 # preceding white space is ignored
(?:                 # the optional ID segment
(?P<id>\d+)         # ... must consist of an ID
(?:@(?P<ref>\d+))?  # ... and may consist of a reference
\s+                 # ... and must have trailing white space
)?
(?P<cmd>\w+)        # the command is just a alphanumeric word
(?:                 # the optional argument segment
\s+                 # ... ignores preceding white space
(?P<args>.*?)       # ... and matches the rest of the line
)?
\s*$                # trailing white space is ignored
""", re.VERBOSE)

    if os.getenv("KGP_PORT"):
        port = int(os.getenv("KGP_PORT"))
    host = os.getenv("KGP_HOST", host)

    STRING_PATTERN = re.compile(r'^"((?:\\.|[^"])*)"\s*')
    INTEGER_PATTERN = re.compile(r'^(\d+)\s*')
    FLOAT_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*')
    BOARD_PATTERN = _BOARD_PATTERN

    queue = mp.Queue()

    def split(args):
        """
        Parse ARGS as far as possible.

        Returns a list of python objects, each equivalent to the
        elements of ARGS as parsed in order.
        """
        upto = 0
        parsed = []

        while True:
            for pat in (STRING_PATTERN,
                        INTEGER_PATTERN,
                        FLOAT_PATTERN,
                        BOARD_PATTERN):
                match = pat.search(args[upto:])
                if not match:
                    continue

                arg = match.group(1)
                if pat == STRING_PATTERN:
                    parsed.append(re.sub(r'\\(.)', '\\1', arg))
                elif pat == INTEGER_PATTERN:
                    parsed.append(int(arg))
                elif pat == FLOAT_PATTERN:
                    parsed.append(float(arg))
                elif pat == BOARD_PATTERN:
                    parsed.append(Board.parse(arg))
                else:
                    assert(False)

                upto += match.end(0)
                break
            else:
                return parsed

    def handle(read, write):
        id = mp.Value('d', 1)


        def send(cmd, *args, ref=None):
            """
            Send cmd with args to server.

            If ref is not None, add a reference.
            """

            msg = str(int(id.value))
            if ref:
                msg += f'@{ref}'
            msg += " " + cmd

            for arg in args:
                msg += " "
                if isinstance(arg, str):
                    string = re.sub(r'"', '\\"', arg)
                    msg += f'"{string}"'
                else:
                    msg += str(arg)

            if debug:
                print(">", msg, file=sys.stderr)
            msg += "\r\n"
            queue.put(msg)

            with id.get_lock():
                id.value += 2

        def query(state, cid, stop_event):
            """
            Query the agent for moves, with a cooperative stop mechanism.
            """
            if state.is_final():
                return
            last = None
            for move in agent(state):
                if stop_event.is_set():  # Check if the thread should stop
                    break
                if not type(move) is int:
                    raise TypeError("Not a move")
                if move != last:
                    send("move", move + 1, ref=cid)
                    last = move
            else:
                send("yield", ref=cid)

        threads = {}
        stop_flags = {}  # Dictionary to store stop flags for each thread


        def sender():
            while True:
                write(queue.get())
        
        threading.Thread(target=sender).start()

        for line in read():
            start_time = time.time()
            if debug:
                print("<", line.strip(), file=sys.stderr)

            try:
                match = COMMAND_PATTERN.match(line)
                if not match:
                    continue
                cid, ref = None, None
                if match.group('id'):
                    cid = int(match.group('id'))
                if match.group('ref'):
                    ref = int(match.group('ref'))
                cmd = match.group('cmd')
                args = split(match.group('args'))

                if cmd == "kgp":
                    major, _minor, _patch = args
                    if major != 1:
                        send("error", "protocol not supported", ref=cid)
                        raise ValueError()
                    if name:
                        send("set", "info:name", name)
                    if authors:
                        send("set", "info:authors", ",".join(authors))
                    if token:
                        send("set", "auth:token", token)
                    send("mode", "freeplay")
                elif cmd == "state":
                    board = args[0]

                    if cid in threads:
                        continue

                    stop_flags[cid] = Event()  # Create a stop flag for this thread
                    threads[cid] = Thread(
                        name=f'query-{cid}',
                        target=query,
                        args=(board, cid, stop_flags[cid])
                    )
                    threads[cid].start()
                    
                elif cmd == "stop":
                    if ref and ref in threads:
                        stop_flags[ref].set()  # Signal the thread to stop
                        threads[ref].join()  # Wait for the thread to finish
                        threads.pop(ref, None)
                        stop_flags.pop(ref, None)
                elif cmd == "ok":
                    pass    # ignored
                elif cmd == "error":
                    pass    # ignored
                elif cmd == "ping":
                    if len(args) >= 1:
                        send("pong", args[0], ref=cid)
                    else:
                        send("pong", ref=cid)
                    end_time = time.time()
                    print(f"PING: {((end_time -start_time)*1000):.4f} ms, {start_time}")
                elif cmd == "goodbye":
                    return
            except ValueError:
                pass
            except TypeError:
                pass

    if host.startswith("ws"):
        assert 'websocket' in sys.modules,\
            "websocket library couldn't be loaded"

        ws = websocket.WebSocket(enable_multithread=True)
        ws.connect(host)
        def lines():
            try:
                while True:
                    yield ws.recv()
            except websocket._exceptions.WebSocketConnectionClosedException:
                pass
        handle(lines, ws.send)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setblocking(True)
            sock.connect((host, port))
            with sock.makefile(mode='rw') as pseudo:
                def write(msg):
                    try:
                        pseudo.write(msg)
                        pseudo.flush()
                    except BrokenPipeError:
                        print("Connection closed by the server.", file=sys.stderr)
                        return
                handle(lambda: pseudo, write)

# Local Variables:
# indent-tabs-mode: nil
# tab-width: 4
# End:
