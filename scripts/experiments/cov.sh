#!/bin/bash

set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 <NAME> <TEST_CLASS> <RUNS>"
  exit 1
fi

pushd `dirname $0` > /dev/null
SCRIPT_DIR=`pwd`
popd > /dev/null

JQF_DIR="$SCRIPT_DIR/../.."
JQF_REPRO="$JQF_DIR/bin/jqf-repro -i"
NAME=$1
TEST_CLASS="edu.berkeley.cs.jqf.examples.$2"
RUNS="$3"
  

export JVM_OPTS="$JVM_OPTS -Djqf.repro.logUniqueBranches=true"

for e in $(seq $RUNS); do
  ZEST_OUT_DIR="$NAME-zest-results-$e"
  EI_OUT_DIR="$NAME-ei-results-$e"

  $JQF_REPRO -c $($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator   $ZEST_OUT_DIR/corpus/* 2>/dev/null | grep "^# Cov" | sort | uniq > $ZEST_OUT_DIR/cov-all.log 
  $JQF_REPRO -c $($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator   $EI_OUT_DIR/corpus/* 2>/dev/null | grep "^# Cov" | sort | uniq > $EI_OUT_DIR/cov-all.log
done

export JVM_OPTS="$JVM_OPTS -Djqf.repro.ignoreInvalidCoverage=true"

for e in $(seq $RUNS); do
  ZEST_OUT_DIR="$NAME-zest-results-$e"
  EI_OUT_DIR="$NAME-ei-results-$e"

  $JQF_REPRO -c $($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator   $ZEST_OUT_DIR/corpus/* 2>/dev/null | grep "^# Cov" | sort | uniq > $ZEST_OUT_DIR/cov-all.log 
  $JQF_REPRO -c $($JQF_DIR/scripts/examples_classpath.sh) $TEST_CLASS testWithGenerator   $EI_OUT_DIR/corpus/* 2>/dev/null | grep "^# Cov" | sort | uniq > $EI_OUT_DIR/cov-all.log
done
