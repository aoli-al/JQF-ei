import os
from configs import *
from visualize import *
import re

def build_corpus_map(path: str) -> Dict[str, str]:
    pattern = re.compile(r"Saved.*corpus/(id_\d+) src:(\d+),.*")
    mapping = {}
    with open(os.path.join(path, "fuzz.log")) as f:
        for line in f:
            result = pattern.match(line)
            if result:
                mapping[result.group(1)] = "id_" + result.group(2)
    return mapping

def process(base_dir: str):
    for dataset in DATASET:
        only_ei_cov_data = set([item[11:] for item in process_cov_data(os.path.join(base_dir, "processed", f"{dataset}-only-ei-fast-cov-all.txt"))])
        for i in range(10):
            expreiment_folder = os.path.join(
                base_dir, f"{dataset}-ei-fast-results-{i}")
            corpus_coverage_folder = os.path.join(expreiment_folder, "corpus_coverage")
            if not os.path.exists(corpus_coverage_folder):
                continue

            mapping = build_corpus_map(expreiment_folder)

            for item in sorted(os.listdir(corpus_coverage_folder)):
                index = item.split(".")[0]
                if index not in mapping:
                    continue

                cov_data = process_cov_data(os.path.join(corpus_coverage_folder, item))
                parent_cov_data = process_cov_data(os.path.join(corpus_coverage_folder, mapping[index] + ".txt"))
                intersection = cov_data.intersection(only_ei_cov_data) - parent_cov_data
                if len(intersection) > 100:
                    print("Index: ", index)
                    print("Parent: ", mapping[index])
                    print(len(intersection))
                    if "5803" in index:
                        for line in intersection:
                            print(line)


if __name__ == "__main__":
    process(sys.argv[1])

