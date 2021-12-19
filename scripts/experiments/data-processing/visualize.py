import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def p2f(value: str) -> float:
    return float(value.strip('%'))

def process_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path, sep=",", skipinitialspace=True,
                       converters={"valid_cov": p2f, "map_size": p2f})
    data['# unix_time'] -= data["# unix_time"][0]
    return data

def generate_valid_cov_fig(path: str, data: pd.DataFrame):
    sns.lineplot(x="# unix_time", y="valid_cov", data=data)
    plt.savefig(path, dpi=300)

def main():
    path = sys.argv[1]
    data = process_data(path)
    out_dir = os.path.dirname(path)
    generate_valid_cov_fig(os.path.join(out_dir, "valid_cov.pdf"), data)

if __name__ == "__main__":
    main()
