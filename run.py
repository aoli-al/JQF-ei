#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import multiprocessing

def run(algo: str, method: str) -> bool:
    command = f'JVM_OPTS="-DuseFastNonCollidingCoverageInstrumentation=true" ./bin/jqf-{algo} -c $(./scripts/examples_classpath.sh)  edu.berkeley.cs.jqf.examples.readorder.TreeProcessorTest {method}'
    proc = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 1 if proc.returncode == 1 else 0

if __name__ == "__main__":
    algos = ["ei", "zest"]
    methods = ["testWithGeneratorRTL", "testWithGeneratorLTR"]
    ITER = 1000

    for algo in algos:
        for method in methods:
            success = 0
            with multiprocessing.Pool(10) as pool:
                result = pool.starmap(run, [(algo, method)] * ITER)
            print(f"Algorithm: {algo}, Method: {method}, Success: {sum(result)/ITER * 100}%")


