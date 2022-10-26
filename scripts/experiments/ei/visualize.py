import sys
import os
from typing import Dict, Iterator, List, Any, Set
import numpy as np
import pandas as pd
import seaborn as sns
import re
import sns_configs
from matplotlib.patches import Patch


def p2f(value: str) -> float:
    return float(value.strip('%'))

def log_scale_index(max: int) -> Iterator[int]:
    idx = 1
    while idx < max:
        yield idx
        if idx > 500:
            idx += 1000
        else:
            idx *= 2

def name_converter(value: str) -> int:
    return int(value.split("_")[1])


def load_processing_time_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(path, "results.csv"), sep=",", names=["case", "result", "class", 'time'],
                       converters={"case": name_converter}, skiprows=10)
    experiment_name = os.path.basename(path)
    algorithm = "-".join(experiment_name.split('-')[1:-2])
    algorithm = map_algorithm(algorithm)
    data['algorithm'] = [algorithm] * data.shape[0]
    return data

def map_algorithm(algo: str) -> str:
    if algo == "ei-fast":
        return "Zest + EI"
    if algo == "zest-fast":
        return "Zest"
    return "EI"

def color_mapping(algo: str) -> str:
    pass

def process_plot_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(path, "plot_data"), sep=",", skipinitialspace=True,
                       converters={"valid_cov": p2f, "map_size": p2f})
    data['# unix_time'] -= data["# unix_time"][0]
    data['# unix_time'] /= 60
    data['total_inputs'] = data['valid_inputs'] + data['invalid_inputs']
    data['total_inputs'] -= data["total_inputs"][0]
    x_axis = "total_inputs"
    experiment_name = os.path.basename(path)
    algorithm = "-".join(experiment_name.split('-')[1:-2])
    algorithm = map_algorithm(algorithm)

    x_axis = "# unix_time"
    time_based_data = data.copy().drop_duplicates(
        keep='first', subset=[x_axis])
    time_based_data = time_based_data.set_index(x_axis).reindex(
        log_scale_index(time_based_data[x_axis].max())).interpolate().reset_index()
    time_based_data['algorithm'] = [algorithm] * time_based_data.shape[0]


    x_axis = "total_inputs"
    # count_based_data = data.copy().drop_duplicates(
    #     keep='first', subset=[x_axis])
    # count_based_data = count_based_data.set_index(x_axis).reindex(
    #     range(0, count_based_data[x_axis].max(), 50)).interpolate().reset_index()
    # count_based_data['algorithm'] = [algorithm] * count_based_data.shape[0]


    return time_based_data, None

def process_cov_data(path: str) -> Set[str]:
    with open(path) as f:
        return set(f.readlines())

def generate_plot_data_base(path: str, data: pd.DataFrame, x_axis: str, y_axis: str, step=1, x_label: str = None, y_label: str = None):
    print(x_axis, y_axis)
    axis = sns.lineplot(x=x_axis, y=y_axis, hue='algorithm',
                        hue_order=sorted(data['algorithm'].unique()), data=data)
    leg = axis.legend()
    leg_lines = leg.get_lines()
    axis.lines[0].set_linestyle("--")
    leg_lines[0].set_linestyle("--")
    axis.lines[1].set_linestyle("-.")
    leg_lines[1].set_linestyle("-.")
    if x_label:
        axis.set(xlabel = x_label)
    if y_label:
        axis.set(ylabel = y_label)
    fig = axis.get_figure()
    fig.savefig(path, bbox_inches='tight', pad_inches=0.1)
    fig.clf()

def generate_valid_coverage_over_time(path: str, data: pd.DataFrame, step=1):
    generate_plot_data_base(path, data, "# unix_time", "valid_covered_probes", step)

def generate_all_coverage_over_time(path: str, data: pd.DataFrame, step=1):
    generate_plot_data_base(path, data, "# unix_time", "all_covered_probes", step, "Time (min)", "Branch Coverage")

def generate_total_inputs_over_time(path: str, data: pd.DataFrame, step=1):
    generate_plot_data_base(path, data, "# unix_time", "total_inputs", step, "Time (min)", "Total Inputs")

def generate_valid_coverage_over_total_inputs(path: str, data: pd.DataFrame, step=1):
    generate_plot_data_base(path, data, "total_inputs", "valid_covered_probes", step)

def generate_all_coverage_over_total_inputs(path: str, data: pd.DataFrame, step=1):
    generate_plot_data_base(path, data, "total_inputs", "all_covered_probes", step)

def generate_corpus_exec_time(path: str, data: pd.DataFrame):
    bins = 20
    axis = sns.histplot(data=data, x="time", hue="algorithm", multiple="dodge", bins=bins, log_scale=(False, True),
                        hue_order=sorted(data['algorithm'].unique()))

    textures = ['/', '*', 'o']
    for i, bar in enumerate(axis.patches):
        bar.set_hatch(textures[i // bins])

    # leg = axis.legend()

    patch_1 = Patch(label='EI', hatch=textures[2], facecolor=sns_configs.colors[0])
    patch_2 = Patch(label='Zest', hatch=textures[1], facecolor=sns_configs.colors[1])
    patch_3 = Patch(label='Zest + EI', hatch=textures[0], facecolor=sns_configs.colors[2])

    axis.set(xlabel = "Execution Time (ms)", ylabel = "Count")


    # leg = axis.legend()
    # print(leg)
    # leg_lines = leg.get_lines()
    # leg_lines[5].set_linestyle(":")

    fig = axis.get_figure()
    axis.legend(handles=[patch_1, patch_2, patch_3], loc='upper right')
    fig.savefig(path, bbox_inches='tight', pad_inches=0.1)
    fig.clf()
    # generate_plot_data_base(path, data, "case", "time", 1)

def show_values_on_bars(axs):
    def _show_on_single_plot(ax):
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height() + 10
            value = str(int(p.get_height()))
            ax.text(_x, _y, value, ha="center")

    if isinstance(axs, np.ndarray):
        for _, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)

def generate_total_coverage_bar(path: str, data: Dict[str, List[Any]]):
    axis = sns.barplot(x="type", y="value", hue="algo", data=data)
    show_values_on_bars(axis)
    fig = axis.get_figure()
    fig.savefig(path)
    fig.clf()



