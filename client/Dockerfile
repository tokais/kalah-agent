# We use the PyPy3 container: https://hub.docker.com/_/pypy.  PyPy
# (https://www.PyPy.org/)is an alternative Python interpreter that is
# usually faster than the conventional (CPython) interpreter.
#
# Alternativly, if you know you want to use the official CPython
# interpreter, use this base container: https://hub.docker.com/_/python.
FROM docker.io/library/pypy:3

# This will be our working directory within the container.
WORKDIR /usr/src/app

# Copy everything from this actual directory into the working
# directory within the container.
COPY . .

# Start our agent.py using the PyPy3 interpreter.  No arguments are
# necessary, we assume the client connects via TCP to localhost:2761.
CMD [ "pypy3", "./agent.py" ]
