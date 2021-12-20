import sys
import os
import pandas as pd
import seaborn as sns


def p2f(value: str) -> float:
    return float(value.strip('%'))

def process_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(path, "plot_data"), sep=",", skipinitialspace=True,
                       converters={"valid_cov": p2f, "map_size": p2f})
    data['# unix_time'] -= data["# unix_time"][0]
    data['total_inputs'] = data['valid_inputs'] + data['invalid_inputs']
    data = data.set_index("total_inputs").reindex(
        range(1, data.total_inputs.max())).interpolate().reset_index()
    algorithm = os.path.basename(path).split('-')[1]
    data['algorithm'] = [algorithm] * data.shape[0]
    return data

def generate_valid_cov_fig(path: str, data: pd.DataFrame, step=1):
    data = data[::step]
    axis = sns.lineplot(x="total_inputs", y="valid_cov", hue='algorithm',
                        hue_order=sorted(data['algorithm'].unique()), data=data)
    fig = axis.get_figure()
    fig.savefig(path)
    fig.clf()

def main():
    path = sys.argv[1]
    data = process_data(path)
    generate_valid_cov_fig(os.path.join(path, "valid_cov.pdf"), data)

if __name__ == "__main__":
    main()
