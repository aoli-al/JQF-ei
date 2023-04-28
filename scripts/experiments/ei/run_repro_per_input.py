from doctest import Example
import subprocess
from configs import *
import sys
import os
from pathlib import Path
from typing import List
from multiprocessing import Pool


EXAMPLES_DIR = os.path.join(Path(__file__).resolve().parent, "../../../examples")

def call(args: List[str]):
    print(args)
    if isinstance(args, str):
        subprocess.check_call(args, cwd=EXAMPLES_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    else:
        subprocess.check_call(args, cwd=EXAMPLES_DIR)

def run(path: str, task: str):
    cpu = 1 if task == "perf" else 15
    with Pool(cpu) as pool:
        pool.map(call, generate_tasks(path, task))


def generate_tasks(base_path: str, mode: str):
    for dataset in DATASET:
        for algorithm in ALGORITHM:
            for generator in GENERATOR:
                for idx in range(1, 10):
                    path = os.path.join(base_path, f"{dataset}-{algorithm}-{generator}-results-{idx}")
                    if not os.path.exists(path):
                        continue
                    corpus_dir = os.path.join(path, "corpus")
                    if mode == "perf":
                        if os.path.exists(os.path.join(path, "results.csv")):
                            continue
                        yield ["mvn", "jqf:repro", "-Dengine=repro",
                                f"-Dclass={DATASET_TEST_CLASS_MAPPING[dataset]}",
                                "-Dmethod=testWithGenerator", f"-Dinput={corpus_dir}",
                                f"-DtraceDir={path}", "-DuseFastNonCollidingCoverageInstrumentation=true"]
                    else:
                        yield f"JVM_OPTS=\"-Djqf.repro.logUniqueBranches=true -Djqf.repro.traceDir={path}\" " + \
                                f"{EXAMPLES_DIR}/../bin/jqf-repro -i -c $({EXAMPLES_DIR}/../scripts/experiments/../../scripts/examples_classpath.sh) " + \
                                f"{DATASET_TEST_CLASS_MAPPING[dataset]} testWithGenerator " + \
                                f"{corpus_dir}/* 2> /dev/null | grep \"^# Cov\" | sort | uniq > {path}/cov-all.log"
                    #  yield "-Djqf.repro.logUniqueBranches=true"
                    #  yield ["mvn", "jqf:repro", "-Dengine=repro",
                            #  f"-Dclass={DATASET_TEST_CLASS_MAPPING[dataset]}",
                            #  "-Dmethod=testWithGenerator", f"-Dinput={corpus_dir}",
                            #  f"-DtraceDir={path}", f"-DlogCoverage={corpus_dir}/../tmp.log"]


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
