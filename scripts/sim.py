#!/usr/bin/env python3

import os
import sys
import time
import random
import logging
import itertools

from multiprocessing.pool import Pool, ThreadPool

from rich.logging import RichHandler
from rich.console import Console

import pandas as pd
import hiplot as hip

logger = logging.getLogger(__name__)
console = Console(file=open('var/sim.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

from savvy import BusinessModel


search_params = {
    "iteration": [0],
    "starting_deposits": [1_000_000],
    "growth_pct": [x / 100.0 for x in range(2, 10, 1)],
    "average_user_yield": [x / 100.0 for x in range(5, 20+1, 5)],
    "starting_pol": [0, 100_000, 250_000, 500_000, 1_000_000, 2_000_000],
    "average_protocol_yield": [x / 100.0 for x in range(5, 20+1, 5)],
    "protocol_fee_pct": [x / 100.0 for x in range(10, 50+1, 5)],
    "buyback_rate_pct": [x / 100.0 for x in range(0, 60+1, 5)],
    "expected_apr": [x / 100.0 for x in range(8, 16+1, 1)],
    "monthly_swap_pressure_pct": [x / 100.0 for x in range(40, 100+1, 20)],
}

def run_one(iteration, *args):
    # print(list(zip(search_params.keys(), args)))
    savvy_possibility = BusinessModel(*args)
    # print(savvy_possibility)
    savvy_possibility.run()
    result = {
        "net_zero_12_months": savvy_possibility.net_zero,
        "break_even_month": savvy_possibility.break_even_month,
        "slope": savvy_possibility.slope,
    }
    del savvy_possibility
    return result

def prepare_tasks():
    keys, values = zip(*search_params.items())
    # permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    permutations = [v for v in itertools.product(*values)]
    print(f"Generated {len(permutations)} tasks")
    return permutations

def run_all(tasks):
    results_accumulator = []

    print("Starting simulation")
    start_time = time.time()

    variables = list(search_params.keys())

    # tasks = tasks[:100]

    with Pool(processes=7) as pool:
        results = pool.starmap(run_one, tasks)
        for savvy_possibility, param in zip(results, tasks):
            result = {
                **dict(zip(variables, param)),
                # "net_zero_12_months": savvy_possibility["net_zero_12_months"],
                "break_even_month": savvy_possibility["break_even_month"],
                "slope": savvy_possibility["slope"],
            }

            results_accumulator.append(result)

    end_time = time.time()
    print(f"Finished in {end_time - start_time} seconds")

    return results_accumulator

def convert_to_dataframe(results_accumulator):
    df_values = [r.values() for r in results_accumulator]
    df_columns = results_accumulator[0].keys()
    df = pd.DataFrame(df_values, columns=df_columns)
    return df

def save(df, filename):
    print(f"Writing results to {filename}")
    df.to_csv(filename, index=False)
    print("Done")

def load(filename):
    df = pd.read_csv(filename)
    if 'iteration' in df:
        del df['iteration']
    return df

def plot(df, filename):
    if 'iteration' in df:
        del(df['iteration'])

    # df = df[ df["net_zero_12_months"] > 0 ]
    df = df[ df["break_even_month"] >= 6 ]
    df = df[ df["slope"] > 0]
    # breakpoint()
    # how many rows in df
    print(f"keeping results: {df.shape[0]}")
    h = hip.Experiment.from_dataframe(df)
    # h.parameters_definition["net_zero"].type = hip.ValueType.NUMERIC_LOG
    h.parameters_definition["starting_pol"].type = hip.ValueType.NUMERIC
    h.to_html(filename)

def main():
    results_accumulator = []
    tasks = prepare_tasks()

    # split tasks into chunks of 100k and run sequentially
    task_chunks = [tasks[x:x+100_000] for x in range(0, len(tasks), 100_000)]
    for i, chunk in enumerate(task_chunks):
        print(f"Running chunk {i+1}")
        results = run_all(chunk)
        results_accumulator.extend(results)

    df = convert_to_dataframe(results_accumulator)

    path = os.path.abspath('.')
    save(df, filename=os.path.join(path, "var/results.csv.gz"))
    # df = load(os.path.join(path, "var/results.csv.gz"))
    # breakpoint()
    plot(df, filename=os.path.join(path, "docs/parameters.html"))

if __name__ == "__main__":
    main()
