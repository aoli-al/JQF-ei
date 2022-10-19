#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from typing import Dict, Set
import pandas as pd
from visualize import *
from pytablewriter import MarkdownTableWriter
from configs import *


def write_cov_data(data: Set[str], path: str):
    with open(path, "w") as f:
        for item in data:
            f.write(item)


def generate_cov_table(base_path: str, algorithms: Set[str]):
    cov_all_data = []
    cov_valid_data = []
    cov_all_avg = []
    cov_all_unique = []
    cov_valid_unique = []
    out_folder = os.path.join(base_path, "processed")
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    for dataset in DATASET:
        cov_all = {}
        cov_valid= {}
        cov_all_data.append([dataset])
        cov_all_avg.append([dataset])
        cov_valid_data.append([dataset])
        for algorithm in algorithms:
            all_avg = []
            valid_avg = []
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                print(path)
                if not os.path.exists(path):
                    break
                # print(f"processing: {os.path.basename(path)}")

                result = set(process_cov_data(os.path.join(path, "cov-all.log")))
                all_avg.append(len(result))
                if algorithm not in cov_all:
                    cov_all[algorithm] = set()
                cov_all[algorithm] |= result

                result = set(process_cov_data(os.path.join(path, "cov-valid.log")))
                if algorithm not in cov_valid:
                    cov_valid[algorithm] = set()
                cov_valid[algorithm] |= result
            if "ant" in dataset:
                print(algorithm)
                print(all_avg)
            cov_all_data[-1].append(len(cov_all[algorithm]))
            cov_all_avg[-1].append(int(sum(all_avg) / len(all_avg)))
            cov_valid_data[-1].append(len(cov_valid[algorithm]))

        dataset_all_data = [dataset]
        dataset_valid_data = [dataset]
        for algorithm in algorithms:
            other_all = set()
            other_valid = set()
            for other in algorithms:
                if ("zest" in algorithm and "ei-fast" not in other) or ("ei" in algorithm and "zest" not in other):
                    continue
                other_all |= cov_all[other]
                other_valid |= cov_valid[other]
            only_all = cov_all[algorithm] - other_all
            only_valid = cov_valid[algorithm] - other_valid
            path = os.path.join(base_path, f"{dataset}-{algorithm}-results-0")
            write_cov_data(only_all, os.path.join(out_folder, f"{dataset}-only-{algorithm}-cov-all.txt"))
            write_cov_data(only_valid, os.path.join(out_folder, f"{dataset}-only-{algorithm}-cov-valid.txt"))
            dataset_all_data.append(len(only_all))
            dataset_valid_data.append(len(only_valid))
        cov_all_unique.append(dataset_all_data)
        cov_valid_unique.append(dataset_valid_data)
    writer = MarkdownTableWriter(
        headers = ["Dataset", *algorithms],
        value_matrix = cov_all_data
    )
    writer.write_table()

    writer = MarkdownTableWriter(
        headers = ["Dataset", *algorithms],
        value_matrix = cov_all_avg
    )
    writer.write_table()

    writer = MarkdownTableWriter(
        headers = ["Dataset", *algorithms],
        value_matrix = cov_all_unique
    )
    writer.write_table()
#


def generate_perf_graph(base_path: str, algorithms: Set[str]):
    out_folder = os.path.join(base_path, "figs")
    for dataset in DATASET:
        corpus_based_plot_data = []
        for algorithm in algorithms:
            for idx in range(0, 1):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                execution_time_data = load_processing_time_data(path)
                corpus_based_plot_data.append(execution_time_data)
        corpus_based_plot_data = pd.concat(corpus_based_plot_data, ignore_index=True, sort=False)
        print(corpus_based_plot_data)
        generate_corpus_exec_time(os.path.join(out_folder, f"{dataset}-exec_time.pdf"), corpus_based_plot_data)


def generate_graph(base_path: str, algorithms: Set[str]):
    for dataset in DATASET:
        time_based_plot_data = []
        count_based_plot_data = []
        for algorithm in algorithms:
            time_based_data_per_algo = []
            count_based_data_per_algo = []
            for idx in range(0, 9):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                # print(f"processing: {os.path.basename(path)}")

                time_based_data, count_based_data = process_plot_data(path)
                time_based_data_per_algo.append(time_based_data)
                count_based_data_per_algo.append(count_based_data)

            time_based_plot_data.extend(time_based_data_per_algo)
            count_based_plot_data.extend(count_based_data_per_algo)
        if not time_based_plot_data:
            continue
        out_folder = os.path.join(base_path, "figs")
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        time_based_plot_data = pd.concat(time_based_plot_data, ignore_index=True, sort=False)
        print(time_based_plot_data)
        # count_based_plot_data = pd.concat(count_based_plot_data, ignore_index=True, sort=False)
        generate_total_inputs_over_time(os.path.join(out_folder, f"{dataset}-total_inputs.pdf"), time_based_plot_data)
        #  generate_valid_coverage_over_time(os.path.join(out_folder, f"{dataset}-valid-cov-time.pdf"), time_based_plot_data)
        generate_all_coverage_over_time(os.path.join(out_folder, f"{dataset}-all-cov-time.pdf"), time_based_plot_data)
        #  generate_valid_coverage_over_total_inputs(os.path.join(out_folder, f"{dataset}-valid-cov-input.pdf"), count_based_plot_data)
        #  generate_all_coverage_over_total_inputs(os.path.join(out_folder, f"{dataset}-all-cov-input.pdf"), count_based_plot_data)


def identify_algorithms(path: str) -> List[str]:
    algorithms = set()
    for subdir in os.listdir(path):
        dir_path = os.path.join(path, subdir)
        if os.path.isdir(dir_path):
            algorithm = "-".join(subdir.split("-")[1:-2])
            if algorithm:
                algorithms.add(algorithm)
    print(algorithms)
    return algorithms


def main():
    path = sys.argv[1]
    algorithms = identify_algorithms(path)
    # generate_cov_table(path, algorithms)
    # generate_graph(path, algorithms)
    generate_perf_graph(path, algorithms)

if __name__ == "__main__":
    main()
