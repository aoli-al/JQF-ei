#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from typing import Dict, Set
import pandas as pd
from table_wriper import TableWriter
import pytablewriter
from visualize import *
from configs import *
from functools import reduce
from scipy import stats
import cliffs_delta
import json
import matplotlib.pyplot as plt


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
                for idx in range(0, 7):
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
            if algorithm not in cov_all_union:
                continue
            with open(os.path.join(out_folder, f"{dataset}-{algorithm}-cov-all-intersection.txt"), "w") as f:
                f.writelines(sorted(cov_all_intersection[algorithm]))
            with open(os.path.join(out_folder, f"{dataset}-{algorithm}-cov-all-union.txt"), "w") as f:
                f.writelines(sorted(cov_all_union[algorithm]))

            data = cov_data[dataset][algorithm]
            if not data:
                continue
            cov_all_table_data[-1].append(len(set.union(*data)))
            # print(dataset)
            # print(algorithm)
            # for b in data:
            #     print(len(b))
            cov_all_avg_data[-1].append(int(reduce(lambda a,
                                        b: a + len(b), data, 0) / len(data)))
            cov_all_avg_data[-1].append(cov_all_avg_data[-1][-1] - cov_all_avg_data[-1][1])
    keys = []
    for algo in algorithms:
        keys.append(map_algorithm(algo))
        keys.append("Delta")
    writer = pytablewriter.MarkdownTableWriter(
        headers = ["Dataset", *keys],
        value_matrix =cov_all_avg_data
    )
    write_table(writer, os.path.join(output_folder, "cov-avg-table.tex"))
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
            if "blind" in algorithm:
                continue
            # if "mix" in algorithm:
            #     continue
            time_based_data_per_algo = []
            count_based_data_per_algo = []
            for idx in range(0, 7):
                for base_path in data_dirs:
                    path = os.path.join(base_path, f"{dataset}-{algorithm}-results-{idx}")
                    if not os.path.exists(path):
                        continue
                    time_based_data, count_based_data = process_plot_data(path)
                    if "mix" in path:
                        time_based_data["# unix_time"] += 480
                    time_based_data_per_algo.append(time_based_data)
                    count_based_data_per_algo.append(count_based_data)
                    if "mix" in path:
                        path += "-tmp"
                        time_based_data, count_based_data = process_plot_data(path)
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
        generate_all_coverage_over_time(os.path.join(output_dir, f"{dataset}-all-cov-time.pdf"), time_based_plot_data)

def visualize_cov_distribution(output_dir: str, cov_data: Dict[str, Dict[str, List[Set[str]]]]):
    for dataset, algorithm_map in cov_data.items():
        delta_map = {}
        for algorithm, cov in algorithm_map.items():
            if "mix" in algorithm:
                continue
            if "no-havoc" in algorithm:
                continue
            if "Reversed" in algorithm:
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
        generate_coverage_delta_hist(os.path.join(output_dir, dataset + "-delta-hist.pdf"),
                                        pd.DataFrame(data))


def visualize_mutation_distance_overtime(path: str, saved_only: bool, generators: List[str], algorithms: List[str]):
    data = parse_mutation_distance_data(path, saved_only, generators, algorithms)
    for dataset, dfs in data.items():
        res = sns.scatterplot(dfs, x=dfs.index, y="distance", hue="algorithm")
        res.set(title=dataset)
        plt.show()

def parse_mutation_distance_data(path: str, saved_only: List[bool], generators: List[str], algorithms: List[str]) -> Dict[str, pd.DataFrame]:
    for dataset in DATASET:
        dfs = []
        for algorithm in algorithms:
            for i in range(5):
                for generator in generators:
                    for if_saved in saved_only:
                        data_path = os.path.join(path, f"{dataset}-{algorithm}-{generator}-results-{i}", "mutation.log")
                        if os.path.exists(data_path):
                            data_frame = pd.read_csv(data_path, sep=",", names=["current_len", "parent_len", "distance", "saved", "parent", "id", "file"], na_values=-1)
                            data_frame["algorithm"] = algorithm + "-" + generator + ("-saved_only" if if_saved else "")
                            # data_frame = data_frame[data_frame["distance"] != 0]
                            if if_saved:
                                data_frame = data_frame[data_frame["saved"]]
                            data_frame["max_length"] = np.maximum.reduce(data_frame[['current_len', 'parent_len']].values, axis=1)
                            data_frame["mutation"] = data_frame["distance"] / data_frame["max_length"]
                            data_frame.drop(columns=["current_len", "parent_len", "saved", "parent", "id"])
                            data_frame.dropna(subset = ['mutation'], inplace=True)
                            if not if_saved:
                                data_frame = data_frame.sample(n=100000, random_state=0)
                            dfs.append(data_frame)
        if dfs:
            dfs = pd.concat(dfs)
            dfs.dropna(subset = ['mutation'], inplace=True)
            yield dataset, dfs

def parse_and_visualize_mutation_data(path: str, saved_only: List[bool], generators: List[str], algorithms: List[str]):
    for dataset, dfs in parse_mutation_distance_data(path, saved_only, generators, algorithms):
        res = sns.histplot(dfs,  x="mutation", hue="algorithm", common_norm=False, stat="proportion", bins=20, multiple="dodge", cumulative=False)
        #sns.ecdfplot(dfs, x="mutation", linewidth=1.5, hue="algorithm", stat="proportion")
        res.set(title=dataset)
        plt.show()
    # sns.histplot(data_frame,  x="distance")

def process_mutation_data(path: str, saved_only: List[bool], generators: List[str], algorithms: List[str], df_name: str):
    df_dict = {}
    attributes = ['mutation', 'algorithm']

    for name, df in parse_mutation_distance_data(path, saved_only, generators, algorithms):
        print('processing {}...'.format(name))
        for attribute in attributes:
            if attribute in df_dict:
                # concat
                df_dict[attribute] = pd.concat([df_dict[attribute], df[attribute]], ignore_index=True)
            else:
                df_dict[attribute] = df[attribute]
        # add the benchmark names
        if 'benchmark_name' in df_dict:
            # concat
            tmp_col = pd.Series([name] * len(df))
            df_dict['benchmark_name'] = pd.concat([df_dict['benchmark_name'], tmp_col], ignore_index=True)
        else:
            df_dict['benchmark_name'] = pd.Series([name] * len(df))
    print('creating dataframe...')
    mutation_df = pd.DataFrame(df_dict)
    mutation_df.to_pickle('./{}.pkl'.format(df_name))

def identify_algorithms(paths: List[str]) -> List[str]:
    algorithms = set()
    for path in paths:
        for subdir in os.listdir(path):
            dir_path = os.path.join(path, subdir)
            if "tmp" in subdir:
                continue
            if "no-havoc" in subdir:
                continue
            if "mix-testWithReversedGenerator" in subdir:
                continue
            if os.path.isdir(dir_path):
                algorithm = "-".join(subdir.split("-")[1:-2])
                if algorithm:
                    algorithms.add(algorithm)
    # if "ei-fast" in algorithms:
    #     algorithms.remove("ei-fast")
    # if "mix" in algorithms:
    #     algorithms.remove("mix")
    return algorithms


def main():
    path = sys.argv[1]
    algorithms = identify_algorithms(path)
    # generate_cov_table(path, algorithms)
    # generate_graph(path, algorithms)
    #  generate_perf_graph(path, algorithms)

if __name__ == "__main__":
    main()
