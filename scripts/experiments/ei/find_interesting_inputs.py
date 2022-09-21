import os
from configs import *
from visualize import *

def process(base_dir: str):
    for dataset in DATASET:
        only_ei_cov_data = process_cov_data(os.path.join(base_dir, "processed", f"{dataset}-only-ei-fast-cov-all.txt"))
        for i in range(10):
            corpus_coverage_folder = os.path.join(
                base_dir, f"{dataset}-ei-fast-results-{i}",
                "corpus_coverage")
            if not os.path.exists(corpus_coverage_folder):
                continue
            for item in sorted(os.listdir(corpus_coverage_folder)):
                cov_data = process_cov_data(os.path.join(corpus_coverage_folder, item))
                intersection = cov_data.intersection(corpus_coverage_folder)
                if intersection:
                    print(item)
                    print(len(intersection))


if __name__ == "__main__":
    process(sys.argv[1])

