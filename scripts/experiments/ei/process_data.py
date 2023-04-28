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
from functools import reduce
from scipy import stats
import cliffs_delta
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


def generate_cov_table(paths: str, algorithms: Set[str], output_folder: str) -> Dict[str, Dict[str, List[Set[str]]]]:
    cov_all_table_data = []
    cov_all_avg_data = []
    cov_data = {}
    out_folder = os.path.join(paths[0], "processed")
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    for dataset in DATASET:
        cov_all_union = {}
        cov_all_intersection = {}
        cov_all_table_data.append([dataset])
        cov_all_avg_data.append([dataset])
        cov_data[dataset] = {}
        for algorithm in algorithms:
            cov_data[dataset][algorithm] = []
            for base_path in paths:
                all_avg = []
                for idx in range(0, 10):
                    folder = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                    if not os.path.exists(folder):
                        continue
                    result = process_cov_data(os.path.join(folder, "cov-all.log")).union(
                        process_cov_data(os.path.join(folder + "-tmp", "cov-all.log")))
                    all_avg.append(len(result))
                    cov_data[dataset][algorithm].append(result)
                    if algorithm not in cov_all_union:
                        cov_all_union[algorithm] = set(result)
                        cov_all_intersection[algorithm] = set(result)
                    cov_all_union[algorithm] |= result
                    cov_all_intersection[algorithm] = cov_all_intersection[algorithm].intersection(result)

            data = cov_data[dataset][algorithm]
            cov_all_table_data[-1].append(len(set.union(*data)))
            # print(dataset)
            # print(algorithm)
            # for b in data:
            #     print(len(b))
            cov_all_avg_data[-1].append(int(reduce(lambda a,
                                        b: a + len(b), data, 0) / len(data)))


        # Print statistical results
        # [a, b, *rst] = cov_data[dataset].values()
        # a = [len(x) for x in a]
        # b = [len(x) for x in b]
        # result = stats.ttest_ind(a, b)
        # avg_a = sum(a) / len(a)
        # avg_b = sum(b) / len(b)

        # cov_all_avg_data[-1].append("{:2.1f}%".format((avg_a - avg_b) / (avg_a) * 100))
        # cov_all_avg_data[-1].append(cliffs_delta.cliffs_delta(a, b)[0])
        # if result.pvalue < 0.01:
        #     cov_all_avg_data[-1].append("<0.01".format(result.pvalue))
        # else:
        #     cov_all_avg_data[-1].append("{:1.2f}".format(result.pvalue))





    print("Cov-All")
    # cov_summary = []
    # for idx in range(len(cov_all_table_data)):
    #     cov_summary.append([*cov_all_table_data[idx], *cov_all_avg_data[idx][1:]])

    # writer = TableWriter(
    #     headers = ["Dataset", *[map_algorithm(algo) for algo in algorithms], *[map_algorithm(algo) for algo in algorithms]],
    #     value_matrix = cov_summary
    # )
    # write_table(writer, os.path.join(output_folder, "cov-total-table.tex"))

    print("Cov-Avg")
    writer = TableWriter(
        headers = ["Dataset", *[map_algorithm(algo) for algo in algorithms], "Improvement", "\sigma", "p"],
        value_matrix =cov_all_avg_data
    )
    write_table(writer, os.path.join(output_folder, "cov-avg-table.tex"))


    # print("Cov-Unique-Union")
    # writer = TableWriter(
    #     headers = ["Dataset", *[map_algorithm(algo) for algo in  algorithms]],
    #     value_matrix = cov_unique_union
    # )
    # write_table(writer, os.path.join(output_folder, "cov-unique-union-table.tex"))

    # print("Cov-Unique-Intersection")
    # writer = TableWriter(
    #     headers = ["Dataset", *[map_algorithm(algo) for algo in  algorithms]],
    #     value_matrix = cov_unique_intersection
    # )
    # write_table(writer, os.path.join(output_folder, "cov-unique-intersection-table.tex"))
    return cov_data
#


def write_table(writer: TableWriter, path: str):
    result = writer.dumps()
    # result = result.replace("array", "tabular")
    # with open(path, "w") as f:
    #     f.write(result)
    writer.write_table()


def generate_perf_graph(data_dirs: List[str], algorithms: Set[str], out_folder: str, out_name: str):
    for dataset in DATASET:
        corpus_based_plot_data = []
        for algorithm in algorithms:
            for idx in range(0, 10):
                for base_path in data_dirs:
                    path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                    if not os.path.exists(path):
                        break
                    execution_time_data = load_processing_time_data(path)
                    corpus_based_plot_data.append(execution_time_data)
        corpus_based_plot_data = pd.concat(corpus_based_plot_data, ignore_index=True, sort=False)
        generate_corpus_exec_time(os.path.join(
            out_folder, f"{dataset}-{out_name}.pdf"), corpus_based_plot_data)


def generate_graph(data_dirs: List[str], algorithms: Set[str], output_dir: str):
    for dataset in DATASET:
        time_based_plot_data = []
        count_based_plot_data = []
        for algorithm in algorithms:
            if "mix" in algorithm:
                continue
            time_based_data_per_algo = []
            count_based_data_per_algo = []
            for idx in range(0, 10):
                for base_path in data_dirs:
                    path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                    if not os.path.exists(path):
                        continue
                    time_based_data, count_based_data = process_plot_data(path)
                    if (time_based_data["# unix_time"].values[-1] < 4310):
                        print(f"{dataset}-{algorithm}-{idx} ERROR!")
                    time_based_data_per_algo.append(time_based_data)
                    count_based_data_per_algo.append(count_based_data)

            time_based_plot_data.extend(time_based_data_per_algo)
            count_based_plot_data.extend(count_based_data_per_algo)
        if not time_based_plot_data:
            continue
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        time_based_plot_data = pd.concat(
            time_based_plot_data, ignore_index=True, sort=False)
        generate_total_inputs_over_time(os.path.join(
            output_dir, f"{dataset}-total_inputs.pdf"), time_based_plot_data)
        print(dataset)
        generate_all_coverage_over_time(os.path.join(output_dir, f"{dataset}-all-cov-time.pdf"), time_based_plot_data)

def visualize_cov_distribution(output_dir: str, cov_data: Dict[str, Dict[str, List[Set[str]]]]):
    for dataset, algorithm_map in cov_data.items():
        delta_map = {}
        for algorithm, cov in algorithm_map.items():
            if "mix" in algorithm:
                continue
            if "no-havoc" in algorithm:
                continue
            delta = 1
            if "zest" in algorithm:
                delta = -1
            for run in cov:
                for line in run:
                    if line not in delta_map:
                        delta_map[line] = 0
                    delta_map[line] += delta
        data = list(delta_map.values())
        data = list(filter((0).__ne__, data))
        print(len(data))
        generate_coverage_delta_hist(os.path.join(output_dir, dataset + "-delta-hist.pdf"),
                                        pd.DataFrame(data))


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
    # algorithms.remove("ei-no-havoc")
    if "mix" in algorithms:
        algorithms.remove("mix")
    return algorithms


def main():
    path = sys.argv[1]
    algorithms = identify_algorithms(path)
    # generate_cov_table(path, algorithms)
    # generate_graph(path, algorithms)
    #  generate_perf_graph(path, algorithms)

if __name__ == "__main__":
    main()
