#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
from visualize import process_data, generate_valid_cov_fig


DATASET = {"ant", "maven", "bcel", "rhino", "closure"}

ALGORITHM = {"zest", "ei"}

def generate(base_path: str):
    for dataset in DATASET:
        results = []
        for algorithm in ALGORITHM:
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                print(f"processing: {os.path.basename(path)}")
                data = process_data(path)
                results.append(data)
                generate_valid_cov_fig(os.path.join(path, "valid_cov.pdf"), data)
        if not results:
            continue
        merged_data = pd.concat(results, ignore_index=True, sort=False)
        generate_valid_cov_fig(os.path.join(base_path, "figs",
                                            f"{dataset}-valid_cov.pdf"), merged_data)


def main():
    path = sys.argv[1]
    generate(path)

if __name__ == "__main__":
    main()
