#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
from visualize import process_plot_data, generate_plot_data_fig, process_cov_data, generate_cov_fig


DATASET = {"ant", "maven", "bcel", "rhino", "closure"}

ALGORITHM = {"zest", "ei"}

def generate(base_path: str):
    for dataset in DATASET:
        plot_data = []
        cov_data = {
            "algo": [],
            "type": [],
            "value": []
        }
        for algorithm in ALGORITHM:
            plot_data_per_algo = []
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                print(f"processing: {os.path.basename(path)}")

                data = process_plot_data(path)
                plot_data_per_algo.append(data)

                cov_all = process_cov_data(os.path.join(path, "cov-all.log"))
                cov_valid = process_cov_data(os.path.join(path, "cov-valid.log"))

                cov_data["algo"].append(algorithm)
                cov_data["type"].append("all")
                cov_data["value"].append(len(cov_all))
                cov_data["algo"].append(algorithm)
                cov_data["type"].append("valid")
                cov_data["value"].append(len(cov_valid))

            min_length = min([d.shape[0] for d in plot_data_per_algo])
            plot_data.extend([d[:min_length:min_length // 1000] for d in plot_data_per_algo])
        if not plot_data:
            continue
        out_folder = os.path.join(base_path, "figs")
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        merged_data = pd.concat(plot_data, ignore_index=True, sort=False)
        generate_plot_data_fig(os.path.join(out_folder,
                                            f"{dataset}-plot_data.pdf"), merged_data)
        generate_cov_fig(os.path.join(out_folder,
                                      f"{dataset}-cov.pdf"), cov_data)


def main():
    path = sys.argv[1]
    generate(path)

if __name__ == "__main__":
    main()
