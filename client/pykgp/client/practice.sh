#!/bin/sh
set -e

PY=python3
if type pypy3 >/dev/null 2>/dev/null
then
    PY=pypy3
fi

# Check if the websocket library has been installed
$PY - <<EOF
try:
       import websocket
except ModuleNotFoundError:
       import sys
       print("""It appears the websocket library couldn't be found.

Make sure you have installed the library for Python 3.  Most
distributions provide a package for the library.  E.g.

- Debian-Based systems: python3-websocket
- RedHat-Based systems: python3-websocket-client
- Alpine: py3-websocket-client

You may also consider setting up a virtual envirionment and installing
the depdendency locally.  See
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment.

More information can be found on the PyPi archive:
https://pypi.org/project/websocket-client/.
""", end="", file=sys.stderr)
       exit(1)
EOF

# If the last command did not fail, we proceed to invoke the agent
# with the USE_WEBSOCKET environmental variable, which the default
# implementation uses to connect to kalah.kwarc.info.
USE_WEBSOCKET=t exec "$PY" ./agent.py
