#!/bin/sh
set -e

# Author: Philip Kaludercic <philip.kaludercic@fau.de>
# Time-stamp: <2023-01-12 12:17:20 oj14ozun>
#
# A modified "prepare.sh" script for the AI1 Kalah tournament that
# generates a .zip archive instead of a tarball.
  
die() {
    >/dev/stderr echo "Fatal: $1"
    exit 1
}

WRAP="cat"
if type fmt >/dev/null 2>&1
then
    # We will only use fmt to wrap warnings, if it is installed,
    # otherwise we revert to cat.
    WRAP="fmt"
fi

HAD_WARNINGS=no
warn() {
    echo "Warning: $1" | >/dev/stderr "$WRAP"
    HAD_WARNINGS=yes
}

if [ ! -f "Dockerfile" ]
then
    die "Each submission requires a Dockerfile."
fi

if type podman >/dev/null 2>&1
then
    >/dev/stderr echo "Podman is installed.  We will try and build your Dockerfile."
    podman build .
elif type docker >/dev/null 2>&1
then
    >/dev/stderr echo "Docker is installed.  We will try and build your Dockerfile."
    docker build .
fi

if [ ! -f "ABOUT" ]
then
    die "Each submission requires an ABOUT file."
fi

if [ ! -s "ABOUT" ]
then
    warn "Are you sure you want to submit an empty ABOUT file?"
fi

if ! awk -v fmt="$WRAP" '
function warn(msg) {
  printf("Warning: %s (Line %d)\n", msg, NR) | fmt
  close(fmt)
  had_warnings = 1
}

/\[[^[:space:]]*] We will not check this box/ {
  warn("Are you sure you correctly read all the checkboxes 
in the ABOUT file?")
}

/WRITEME/ {
  warn("There are still a few unfinished WRITEMEs in your 
ABOUT file.  Are you sure you finished it?")
}

(/be15piel/ || /kl15chee/ || /se45hell/) && !be15piel {
  warn("Are you sure you sure the list of participants the ABOUT file is correct?")
  be15piel = 1 # avoid printing this message more than once
}

END {
  if (had_warnings) exit 1;
}' ABOUT
then
    HAD_WARNINGS=yes
fi

if ! type zip >/dev/null 2>&1
then
    die "This script requires zip to be installed"
fi

zip -r submission.zip .

echo                            # empty line
echo "\$ ls -lh submission.zip"
ls -lh submission.zip
echo                            # empty line

if [ "$HAD_WARNINGS" = "yes" ]
then
    echo "Your submission has been successfully prepared \
(DESPITE GENERATING WARNINGS!) and can be found in \
submission.tar.gz.  Upload this file to StudOn."
else
    echo "Your submission has been successfully prepared and can be \
found in submission.tar.gz.  Upload this file to StudOn."
fi | "$WRAP"
