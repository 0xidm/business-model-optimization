#!/usr/bin/env python3

import os
import time
import random
from multiprocessing.pool import Pool, ThreadPool

import pandas as pd
import hiplot as hip

from savvy import BusinessModel


def run_one(iteration, *params):
    savvy_possibility = BusinessModel(*params)
    savvy_possibility.run()
    return savvy_possibility

def prepare_tasks():
    tasks = []
    print("Generating tasks")
    for iteration in [0]: # there is no variability so we can run a single iteration
        for starting_deposits in 1_000_000, 1_500_000, 2_500_000, 5_000_000:
            for growth_pct in range(2, 16, 2):
                for average_user_yield in range(5, 20, 5):
                    for starting_pol in 0, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000:
                        for average_protocol_yield in range(10, 30, 5):
                            for protocol_fee_pct in range(5, 25, 5):
                                for buyback_rate_pct in range(10, 60, 10):
                                    for expected_apr in range(4, 20, 4):
                                        this_task = [
                                            iteration,
                                            starting_deposits,
                                            growth_pct,
                                            average_user_yield,
                                            starting_pol,
                                            average_protocol_yield,
                                            protocol_fee_pct,
                                            buyback_rate_pct,
                                            expected_apr,
                                        ]
                                        tasks.append(this_task)
    print(f"Generated {len(tasks)} tasks")
    return tasks

def run_all(tasks):
    results_accumulator = []

    print("Starting simulation")
    start_time = time.time()

    variables = [
        "iteration",
        "starting_deposits",
        "growth_pct",
        "average_user_yield",
        "starting_pol",
        "average_protocol_yield",
        "protocol_fee_pct",
        "buyback_rate_pct",
        "expected_apr",
    ]

    with Pool(processes=7) as pool:
        results = pool.starmap(run_one, tasks)
        for savvy_possibility, param in zip(results, tasks):
            result = {
                **dict(zip(variables, param)),
                "net_zero": savvy_possibility.net_zero,
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
    del df['iteration']
    return df

def plot(df, filename):
    h = hip.Experiment.from_dataframe(df)
    h.parameters_definition["net_zero"].type = hip.ValueType.NUMERIC_LOG
    h.to_html(filename)

def main():
    tasks = prepare_tasks()
    results_accumulator = run_all(tasks)
    df = convert_to_dataframe(results_accumulator)

    path = os.path.abspath('.')
    save(df, filename=os.path.join(path, "var/results.csv.gz"))
    plot(df, filename=os.path.join(path, "docs/parameters.html"))

if __name__ == "__main__":
    main()
