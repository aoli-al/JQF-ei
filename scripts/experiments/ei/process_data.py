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

def highlight_data(data):
    row_max = max(data[-1][1:])
    for i in range(len(data[-1][1:])):
        if data[-1][i + 1] == row_max:
            data[-1][i + 1] = "\\cellgreen{" + str(data[-1][i + 1]) + "}"


def generate_cov_table(paths: str, algorithms: Set[str], output_folder: str):
    cov_all_data = []
    cov_valid_data = []
    cov_all_avg = []
    cov_unique_union = []
    cov_unique_intersection = []
    out_folder = os.path.join(paths[0], "processed")
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    for dataset in DATASET:
        cov_all_union = {}
        cov_all_intersection = {}
        cov_all_data.append([dataset])
        cov_all_avg.append([dataset])
        cov_valid_data.append([dataset])
        for algorithm in algorithms:
            for base_path in paths:
                all_avg = []
                for idx in range(0, 10):
                    folder = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                    result = process_cov_data(os.path.join(folder, "cov-all.log")).union(
                        process_cov_data(os.path.join(folder + "-tmp", "cov-all.log")))
                    # result = process_cov_data(os.path.join(folder, "cov-all.log"))
                    # if "mix" in algorithm:
                    #     result = process_cov_data(os.path.join(folder + "-tmp", "cov-all.log"))
                    # else:
                    #     result = process_cov_data(os.path.join(folder, "cov-all.log"))
                    all_avg.append(len(result))
                    if algorithm not in cov_all_union:
                        cov_all_union[algorithm] = set(result)
                        cov_all_intersection[algorithm] = set(result)
                    cov_all_union[algorithm] |= result
                    cov_all_intersection[algorithm] = cov_all_intersection[algorithm].intersection(result)

            cov_all_data[-1].append(len(cov_all_union[algorithm]))
            cov_all_avg[-1].append(int(sum(all_avg) / len(all_avg)))
        highlight_data(cov_all_data)
        highlight_data(cov_all_avg)

        only_union_data = [dataset]
        only_intersection_data = [dataset]
        for algorithm in algorithms:
            other_all = set()
            if "mix" in algorithm or "ei" in algorithm:
                # other_all = cov_all_union["zest-fast"]
                other_key = "zest-fast"
            else:
                if "mix" in algorithms:
                    other_key = "mix"
                    # if len(cov_all["mix"]) > len(cov_all["mix-no-havoc"]):
                    #     other_all = cov_all["mix"]
                    # else:
                    #     other_all = cov_all["mix-no-havoc"]
                    # other_all = cov_all["mix-no-havoc"]
                else:
                    # other_all = cov_all_union["ei-fast"]
                    other_key = "ei-fast"
            only_union = cov_all_union[algorithm] - cov_all_union[other_key]
            only_intersection = cov_all_intersection[algorithm] - cov_all_intersection[other_key]
            # write_cov_data(only_all, os.path.join(out_folder, f"{dataset}-only-{algorithm}-cov-all.txt"))
            only_union_data.append(len(only_union))
            only_intersection_data.append(len(only_intersection))
        cov_unique_union.append(only_union_data)
        cov_unique_intersection.append(only_intersection_data)
        highlight_data(cov_unique_union)
        highlight_data(cov_unique_intersection)


    print("Cov-All")
    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in algorithms]],
        value_matrix = cov_all_data
    )
    write_table(writer, os.path.join(output_folder, "cov-total-table.tex"))

    print("Cov-Avg")
    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in algorithms]],
        value_matrix =cov_all_avg
    )
    write_table(writer, os.path.join(output_folder, "cov-avg-table.tex"))


    print("Cov-Unique-Union")
    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in  algorithms]],
        value_matrix = cov_unique_union
    )
    write_table(writer, os.path.join(output_folder, "cov-unique-union-table.tex"))

    print("Cov-Unique-Intersection")
    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in  algorithms]],
        value_matrix = cov_unique_intersection
    )
    write_table(writer, os.path.join(output_folder, "cov-unique-intersection-table.tex"))
#

def write_table(writer: TableWriter, path: str):
    result = writer.dumps()
    result = result.replace("array", "tabular")
    with open(path, "w") as f:
        f.write(result)
    writer.write_table()


def generate_perf_graph(base_path: str, algorithms: Set[str], out_folder: str, out_name: str):
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
        generate_corpus_exec_time(os.path.join(out_folder, f"{dataset}-{out_name}.pdf"), corpus_based_plot_data)


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


def identify_algorithms(paths: List[str]) -> List[str]:
    algorithms = set()
    for path in paths:
        for subdir in os.listdir(path):
            dir_path = os.path.join(path, subdir)
            if "tmp" in subdir:
                continue
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
