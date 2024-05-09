import os
import sys

import pandas as pd
import hiplot as hip


def load(filename):
    df = pd.read_csv(filename)
    return df

def filter(df):
    print("filtering")
    # result = df.query("break_even_month >= 18 and slope > 50")
    result = df.query("break_even_month >= 12")
    print(f"filtered results: {result.shape[0]}")
    return result

def plot(df, filename):
    h = hip.Experiment.from_dataframe(df)
    # h.parameters_definition["net_zero"].type = hip.ValueType.NUMERIC_LOG
    h.parameters_definition["starting_pol"].type = hip.ValueType.NUMERIC
    h.to_html(filename)


if __name__ == "__main__":
    # parse cli arguments
    if len(sys.argv) == 2:
        timestamp = sys.argv[1]
    else:
        # find the directory with the most recent timestamp
        path = os.path.join(os.path.abspath('.'), "var")
        dirs = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
        timestamp = dirs[-1]

    path = os.path.abspath('.')
    df = load(os.path.join(path, f"var/{timestamp}/merged.csv.gz"))
    df = filter(df)
    plot(df, filename=os.path.join(path, f"docs/result-{timestamp}.html"))
