#!/bin/bash

set -e

if [ $# -lt 6 ]; then
  echo "Usage: $0 <NAME> <TEST_CLASS> <IDX> <TIME> <DICT> <SEEDS>"
  exit 1
fi

pushd `dirname $0` > /dev/null
SCRIPT_DIR=$( dirname "$0" )
popd > /dev/null

JQF_DIR="$SCRIPT_DIR/../.."
JQF_EI="$JQF_DIR/bin/jqf-ei"
JQF_ZEST="$JQF_DIR/bin/jqf-zest"
NAME=$1
TEST_CLASS="edu.berkeley.cs.jqf.examples.$2"
IDX=$3
TIME=$4
DICT="$JQF_DIR/examples/target/test-classes/dictionaries/$5"
SEEDS="$JQF_DIR/examples/target/seeds/$6"
SEEDS_DIR=$(dirname "$SEEDS")

e=$IDX

EI_OUT_DIR="$NAME-ei-results-$e"
ZEST_OUT_DIR="$NAME-zest-results-$e"

if [ -d "$JQF_OUT_DIR" ]; then
  echo "Error! There is already a directory by the name of $EI_OUT_DIR"
  exit 3
fi

# Do not let GC mess with fuzzing
export JVM_OPTS="$JVM_OPTS -XX:-UseGCOverheadLimit"

SNAME="$NAME-$e"

screen -S "$SNAME" -dm -t ei_$e
#screen -S "$SNAME" -X screen -t jqf_$e
screen -S "$SNAME" -X screen -t zest_$e
screen -S "$SNAME" -p ei_$e -X stuff "timeout $TIME $JQF_EI -c \$($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator $EI_OUT_DIR^M"
screen -S "$SNAME" -p zest_$e -X stuff "timeout $TIME $JQF_ZEST -c \$($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator $ZEST_OUT_DIR^M"

