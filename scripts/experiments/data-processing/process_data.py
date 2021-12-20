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
            algo_results = []
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                print(f"processing: {os.path.basename(path)}")
                data = process_data(path)
                algo_results.append(data)
                generate_valid_cov_fig(os.path.join(path, "valid_cov.pdf"), data, data.shape[0] // 1000)
            min_length = min([d.shape[0] for d in algo_results])
            results.extend([d[:min_length:min_length // 1000] for d in algo_results])
        if not results:
            continue
        out_folder = os.path.join(base_path, "figs")
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        merged_data = pd.concat(results, ignore_index=True, sort=False)
        generate_valid_cov_fig(os.path.join(out_folder,
                                            f"{dataset}-valid_cov.pdf"), merged_data)


def main():
    path = sys.argv[1]
    generate(path)

if __name__ == "__main__":
    main()
