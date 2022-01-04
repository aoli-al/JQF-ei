import sys
import os
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import seaborn as sns


def p2f(value: str) -> float:
    return float(value.strip('%'))

def process_plot_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(path, "plot_data"), sep=",", skipinitialspace=True,
                       converters={"valid_cov": p2f, "map_size": p2f})
    data['# unix_time'] -= data["# unix_time"][0]
    data['total_inputs'] = data['valid_inputs'] + data['invalid_inputs']
    data = data.set_index("total_inputs").reindex(
        range(1, data.total_inputs.max(), 50)).interpolate().reset_index()
    algorithm = os.path.basename(path).split('-')[1]
    if "fast" in os.path.basename(path):
        algorithm += "-fast"
    data['algorithm'] = [algorithm] * data.shape[0]
    return data

def process_cov_data(path: str) -> List[str]:
    with open(path) as f:
        return f.readlines()

def generate_plot_data_fig(path: str, data: pd.DataFrame, step=1):
    data = data[::step]
    axis = sns.lineplot(x="total_inputs", y="valid_cov", hue='algorithm',
                        hue_order=sorted(data['algorithm'].unique()), data=data)
    fig = axis.get_figure()
    fig.savefig(path)
    fig.clf()

def show_values_on_bars(axs):
    def _show_on_single_plot(ax):
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height()
            value = '{:.2f}'.format(p.get_height())
            ax.text(_x, _y, value, ha="center")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)

def generate_cov_fig(path: str, data: Dict[str, List[Any]]):
    axis = sns.barplot(x="type", y="value", hue="algo", data=data)
    show_values_on_bars(axis)
    fig = axis.get_figure()
    fig.savefig(path)
    fig.clf()


def main():
    path = sys.argv[1]
    data = process_plot_data(path)
    generate_plot_data_fig(os.path.join(path, "valid_cov.pdf"), data)

if __name__ == "__main__":
    main()
