import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def p2f(value: str) -> float:
    return float(value.strip('%'))

def process_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(path, "plot_data"), sep=",", skipinitialspace=True,
                       converters={"valid_cov": p2f, "map_size": p2f})
    data['# unix_time'] -= data["# unix_time"][0]

    data = data[::100] # downsampling

    algorithm = os.path.basename(path).split('-')[1]
    data['algorithm'] = [algorithm] * data.shape[0]
    return data

def generate_valid_cov_fig(path: str, data: pd.DataFrame):
    axis = sns.lineplot(x="# unix_time", y="valid_cov", hue='algorithm', data=data)
    fig = axis.get_figure()
    fig.savefig(path)

def main():
    path = sys.argv[1]
    data = process_data(path)
    generate_valid_cov_fig(os.path.join(path, "valid_cov.pdf"), data)

if __name__ == "__main__":
    main()
