#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from typing import Dict, Set
import pandas as pd
from table_wriper import TableWriter
from visualize import *
from pytablewriter import LatexTableWriter
from configs import *
import json


def write_cov_data(data: Set[str], path: str):
    with open(path, "w") as f:
        for item in data:
            f.write(item)


def generate_cov_table(base_path: str, algorithms: Set[str], output_folder: str):
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
                if not os.path.exists(path):
                    break
                # print(f"processing: {os.path.basename(path)}")

                result = set(process_cov_data(os.path.join(path, "cov-all.log")))
                all_avg.append(len(result))
                if algorithm not in cov_all:
                    cov_all[algorithm] = set()
                cov_all[algorithm] |= result

            cov_all_data[-1].append(len(cov_all[algorithm]))
            cov_all_avg[-1].append(int(sum(all_avg) / len(all_avg)))

        row_max = max(cov_all_data[-1][1:])
        for i in range(len(cov_all_data[-1][1:])):
            if cov_all_data[-1][i + 1] == row_max:
                cov_all_data[-1][i + 1] = "\\cellgreen{" + str(cov_all_data[-1][i + 1]) + "}"

        dataset_all_data = [dataset]
        for algorithm in algorithms:
            other_all = set()
            if "ei" in algorithm:
                other_all = cov_all["zest-fast"]
            else:
                other_all = cov_all["ei-fast"]
            only_all = cov_all[algorithm] - other_all
            path = os.path.join(base_path, f"{dataset}-{algorithm}-results-0")
            write_cov_data(only_all, os.path.join(out_folder, f"{dataset}-only-{algorithm}-cov-all.txt"))
            dataset_all_data.append(len(only_all))
        cov_all_unique.append(dataset_all_data)


    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in algorithms]],
        value_matrix = cov_all_data
    )
    result = writer.dumps()
    result = result.replace("array", "tabular")
    with open(os.path.join(output_folder, "cov-table.tex"), "w") as f:
        f.write(result)
    writer.write_table()

    # writer = MarkdownTableWriter(
    #     headers = ["Dataset", *algorithms],
    #     value_matrix = cov_all_avg
    # )
    # writer.write_table()

    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in  algorithms]],
        value_matrix = cov_all_unique
    )
    writer.write_table()
#


def generate_perf_graph(base_path: str, algorithms: Set[str], out_folder):
    for dataset in DATASET:
        corpus_based_plot_data = []
        for algorithm in algorithms:
            for idx in range(0, 10):
                path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                if not os.path.exists(path):
                    break
                execution_time_data = load_processing_time_data(path)
                corpus_based_plot_data.append(execution_time_data)
        corpus_based_plot_data = pd.concat(corpus_based_plot_data, ignore_index=True, sort=False)
        generate_corpus_exec_time(os.path.join(out_folder, f"{dataset}-exec_time.pdf"), corpus_based_plot_data)


def generate_graph(base_path: str, algorithms: Set[str], output_dir: str):
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
                time_based_data, count_based_data = process_plot_data(path)
                time_based_data_per_algo.append(time_based_data)
                count_based_data_per_algo.append(count_based_data)

            time_based_plot_data.extend(time_based_data_per_algo)
            count_based_plot_data.extend(count_based_data_per_algo)
        if not time_based_plot_data:
            continue
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        time_based_plot_data = pd.concat(time_based_plot_data, ignore_index=True, sort=False)
        generate_total_inputs_over_time(os.path.join(output_dir, f"{dataset}-total_inputs.pdf"), time_based_plot_data)
        generate_all_coverage_over_time(os.path.join(output_dir, f"{dataset}-all-cov-time.pdf"), time_based_plot_data)


def identify_algorithms(path: str) -> List[str]:
    algorithms = set()
    for subdir in os.listdir(path):
        dir_path = os.path.join(path, subdir)
        if os.path.isdir(dir_path):
            algorithm = "-".join(subdir.split("-")[1:-2])
            if algorithm:
                algorithms.add(algorithm)
    return algorithms


def main():
    path = sys.argv[1]
    algorithms = identify_algorithms(path)
    # generate_cov_table(path, algorithms)
    # generate_graph(path, algorithms)
    #  generate_perf_graph(path, algorithms)

if __name__ == "__main__":
    main()
