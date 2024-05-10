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

logger = logging.getLogger(__name__)
console = Console(file=open('var/sim.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

from savvy import BusinessModel

# the order of these params must match BusinessModel constructor
search_params = {
    "iteration": [0],
    "starting_deposits": [1_000_000],
    "starting_growth_pct": [x / 100.0 for x in range(2, 30, 2)],
    "average_user_yield": [x / 100.0 for x in range(7, 11+1, 1)],
    "starting_pol": [0, 500_000, 1_000_000, 2_000_000],
    "average_protocol_yield": [x / 100.0 for x in range(12, 16+1, 1)],
    "protocol_fee_pct": [x / 100.0 for x in range(10, 50+1, 5)],
    "buyback_rate_pct": [x / 100.0 for x in range(10, 100+1, 10)],
    "monthly_swap_pressure_pct": [x / 100.0 for x in range(60, 100+1, 20)],
    "credit_utilization": [0.4, 0.45, 0.5],
    # "credit_utilization": [0.5],
    # "expected_apr": [x / 100.0 for x in range(3, 15+1, 2)],
}

def run_one(iteration, *args):
    savvy_possibility = BusinessModel(*args)
    savvy_possibility.run()
    result = {
        "break_even_month": savvy_possibility.break_even_month,
        "slope": savvy_possibility.slope,
        "f_treasury": savvy_possibility.final_treasury,
        "f_deposits": savvy_possibility.final_deposits,
        "f_sages": savvy_possibility.final_sages,
        "f_tvl": savvy_possibility.final_tvl,
    }
    del savvy_possibility
    return result

def prepare_tasks():
    keys, values = zip(*search_params.items())
    permutations = [v for v in itertools.product(*values)]
    print(f"Generated {len(permutations):_} tasks")
    return permutations

def run_all(tasks, num_processes=7, quick=False):
    results_accumulator = []
    variables = list(search_params.keys())
    start_time = time.time()

    if quick:
        tasks = tasks[:100]

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(run_one, tasks)
        for savvy_possibility, param in zip(results, tasks):
            result = {
                **dict(zip(variables, param)),
                "break_even_month": savvy_possibility["break_even_month"],
                "slope": savvy_possibility["slope"],
                "treasury": savvy_possibility["f_treasury"],
                "deposits": savvy_possibility["f_deposits"],
                "sages": savvy_possibility["f_sages"],
                "tvl": savvy_possibility["f_tvl"],
            }

            results_accumulator.append(result)

    end_time = time.time()
    print(f"Finished in {end_time - start_time} seconds")

    return results_accumulator

def convert_to_dataframe(results_accumulator):
    df_columns = results_accumulator[0].keys()
    df = pd.DataFrame([r.values() for r in results_accumulator], columns=df_columns)
    return df

def save(df, filename):
    print(f"Writing results to {filename}")
    if 'iteration' in df:
        del df['iteration']
    df.to_csv(filename, index=False)
    print("Done")

def sim(num_processes=7, quick=False):
    results_accumulator = []
    tasks = prepare_tasks()

    chunk_size = 100_000
    num_chunks = len(tasks) // chunk_size
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(os.path.abspath('.'), "var", timestamp)
    os.makedirs(path, exist_ok=True)
    print(f"writing to {path}")

    # split tasks into chunks of 100k and run sequentially
    task_chunks = [tasks[x:x+100_000] for x in range(0, len(tasks), 100_000)]
    for i, chunk in enumerate(task_chunks):
        print(f"Running chunk {i}/{num_chunks} with {num_processes} processes")
        results = run_all(chunk, num_processes=num_processes, quick=quick)
        df = convert_to_dataframe(results)
        save(df, filename=os.path.join(path, f"{i:05d}.csv.gz"))
        if quick:
            break


if __name__ == "__main__":
    # parse cli arguments
    num_processes = 7
    if len(sys.argv) > 1:
        num_processes = int(sys.argv[1])
#     sim(num_processes, quick=True)
    sim(num_processes, quick=False)
