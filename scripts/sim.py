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


search_params = {
    "iteration": [0],
    "starting_deposits": [1_000_000],
    "starting_pol": [0, 100_000, 250_000, 500_000, 1_000_000, 2_000_000],
    "protocol_fee_pct": [x / 100.0 for x in range(10, 50+1, 5)],
    "buyback_rate_pct": [x / 100.0 for x in range(0, 100+1, 10)],
    "credit_utilization": [0.5],
    "average_user_yield": [x / 100.0 for x in range(5, 20+1, 5)],
    "average_protocol_yield": [x / 100.0 for x in range(5, 20+1, 5)],
    "monthly_swap_pressure_pct": [x / 100.0 for x in range(0, 100+1, 20)],
    "expected_apr": [x / 100.0 for x in range(9, 16+1, 2)],
    "growth_pct": [x / 100.0 for x in range(1, 15, 1)],
}

def run_one(iteration, *args):
    savvy_possibility = BusinessModel(*args)
    savvy_possibility.run()
    result = {
        "break_even_month": savvy_possibility.break_even_month,
        "slope": savvy_possibility.slope,
        "treasury": savvy_possibility.treasury,
        "deposits": savvy_possibility.deposits,
        "sages": savvy_possibility.sages,
    }
    del savvy_possibility
    return result

def prepare_tasks():
    keys, values = zip(*search_params.items())
    permutations = [v for v in itertools.product(*values)]
    print(f"Generated {len(permutations):_} tasks")
    return permutations

def run_all(tasks, num_processes=7):
    results_accumulator = []
    variables = list(search_params.keys())
    start_time = time.time()
    # tasks = tasks[:100]

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(run_one, tasks)
        for savvy_possibility, param in zip(results, tasks):
            result = {
                **dict(zip(variables, param)),
                "break_even_month": savvy_possibility["break_even_month"],
                "slope": savvy_possibility["slope"],
                "treasury": savvy_possibility["treasury"],
                "deposits": savvy_possibility["deposits"],
                "sages": savvy_possibility["sages"],
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

def sim(num_processes=7):
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
        print(f"Running chunk {i+1}/{num_chunks} with {num_processes} processes")
        results = run_all(chunk, num_processes=num_processes)
        df = convert_to_dataframe(results)
        save(df, filename=os.path.join(path, f"{i:05d}.csv.gz"))


if __name__ == "__main__":
    # parse cli arguments
    num_processes = 7
    if len(sys.argv) > 1:
        num_processes = int(sys.argv[1])
    sim(num_processes)
