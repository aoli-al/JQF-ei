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
    subprocess.call(args, cwd=EXAMPLES_DIR)

def run(path: str):
    with Pool(10) as pool:
        pool.map(call, generate_tasks(path))


def generate_tasks(base_path: str):
    for dataset in DATASET:
        for algorithm in ALGORITHM:
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                print(path)
                if not os.path.exists(path):
                    break
                corpus_dir = os.path.join(path, "corpus")
                output_dir = os.path.join(path, "corpus_coverage")
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                for file_name in sorted(os.listdir(corpus_dir)):
                    input_path = os.path.realpath(os.path.join(corpus_dir, file_name))
                    output_path = os.path.realpath(os.path.join(output_dir, file_name + '.txt'))
                    yield ["mvn", "jqf:repro", "-Dengine=repro",
                           f"-Dclass={DATASET_TEST_CLASS_MAPPING[dataset]}",
                           "-Dmethod=testWithGenerator", f"-Dinput={input_path}",
                           f"-DlogCoverage={output_path}"]


if __name__ == "__main__":
    run(sys.argv[1])