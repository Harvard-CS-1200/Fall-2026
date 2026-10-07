import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time
import random
from collections import Counter, defaultdict

# Reproducibility (feel free to change locally)
random.seed(120)

# Import your HashTable implementations
from ps4 import HashTable, DeterministicHash, RandomHash

#
# IMPORTANT:
# You do NOT need to modify this file for the assignment.
# Implement the non-optimized search/delete in ps4_p1.py.
#

# ----------------------------
# Experiment configuration
# ----------------------------
NUM_TRIALS = 50          # trials per parameter combo
NUM_OPS = 1_000          # operations per trial

# operation mix should sum to 1.0
OP_WEIGHTS = {
    "search": 0.50,
    "insert": 0.40,
    "delete": 0.10,
}

# parameter grid
M_VALUES = [1, 10, 100, 1000]
KEY_MODES = ["employee_id", "salary"]
LAZING_VALUES = [True, False]
HASH_FAMILIES = ["deterministic", "random"]

# universe bounds
U = 10_000_000

# salaries are multiples of $10,000 in [10_000, 10_000_000]
SALARY_STEP = 1000
SALARY_MIN = 10_000
SALARY_MAX = 10_000_000
SALARY_MULT_MIN = SALARY_MIN // SALARY_STEP
SALARY_MULT_MAX = SALARY_MAX // SALARY_STEP


# ----------------------------
# Data generation helpers
# ----------------------------
def draw_salary_multiple():
    mult = random.randint(SALARY_MULT_MIN, SALARY_MULT_MAX)
    return mult * SALARY_STEP


def draw_employee_id():
    return random.randint(1, U)


def choose_action():
    r = random.random()
    cdf = 0.0
    for action, w in OP_WEIGHTS.items():
        cdf += w
        if r < cdf:
            return action
    return "search"


# ----------------------------
# Hash family factory
# ----------------------------
def make_hash_family(name, U, m, seed):
    if name == "deterministic":
        return DeterministicHash(U, m)
    elif name == "random":
        # If your RandomHash doesn't take seed, remove the kwarg here.
        return RandomHash(U, m, seed=seed)
    else:
        raise ValueError("Unknown hash family: " + name)


# ----------------------------
# Single trial
# ----------------------------
def run_one_trial(key_mode, m, lazing, hash_family_name, trial_seed):
    random.seed(trial_seed)

    # Ground truth: multimap key -> Counter of values (tracks multiplicities)
    gt = defaultdict(Counter)

    hf = make_hash_family(hash_family_name, U, m, seed=trial_seed + 17)
    table = HashTable(U, m, hf, lazing)

    # Track which keys currently exist (any count > 0 in gt)
    keys_live = set()

    incorrect = 0
    elapsed = 0

    for _ in range(NUM_OPS):
        action = choose_action()

        if action == "insert":
            eid = draw_employee_id()
            sal = draw_salary_multiple()
            if key_mode == "employee_id":
                k, v = eid, sal
            else:
                k, v = sal, eid

            # Insert into multimap
            gt[k][v] += 1
            keys_live.add(k)

            cur_start = time.perf_counter()
            table.insert(k, v)
            elapsed += time.perf_counter() - cur_start

        elif action == "delete":
            if not keys_live:
                action = "search"

        if action == "delete":
            # Delete any one pair with key k (table may delete any (k, v))
            k = random.choice(tuple(keys_live))

            cur_start = time.perf_counter()
            table.delete(k)
            elapsed += time.perf_counter() - cur_start

            # Reflect one arbitrary (k, v) deletion in gt
            if gt[k]:
                # decrement one arbitrary value count
                any_v = next(iter(gt[k]))          # arbitrary pick
                gt[k][any_v] -= 1
                if gt[k][any_v] <= 0:
                    del gt[k][any_v]
            # if no values remain for k, remove key from live set
            if not gt[k]:
                del gt[k]
                keys_live.discard(k)

        elif action == "search":
            # 50%: search an existing key (if any), else a random (possibly absent) key
            if keys_live and random.random() < 0.5:
                k = random.choice(tuple(keys_live))
            else:
                k = draw_employee_id() if key_mode == "employee_id" else draw_salary_multiple()

            cur_start = time.perf_counter()
            got = table.search(k)
            elapsed += time.perf_counter() - cur_start

            # Multimap correctness:
            # - If k not present in gt: correct iff got is None
            # - If k present: correct iff got is any value with positive count for k
            if k not in gt:
                if got is not None:
                    incorrect += 1
            else:
                if got is None or gt[k][got] <= 0:
                    incorrect += 1

    return elapsed, incorrect


# ----------------------------
# Summaries + plots
# ----------------------------
def summarize_and_plot(df, num_ops_per_trial):
    summary = (
        df.groupby(["Key", "M", "Lazing", "HashFamily"], as_index=False)
          .agg(
              Runs=("Trial", "count"),
              TimeMean_ms=("Runtime (ms)", "mean"),
              TimeStd_ms=("Runtime (ms)", "std"),
              TimeMedian_ms=("Runtime (ms)", "median"),
              IncorrectMean=("IncorrectSearches", "mean"),
              IncorrectStd=("IncorrectSearches", "std"),
          )
    )

    summary["IncorrectRate_%"] = 100.0 * summary["IncorrectMean"] / num_ops_per_trial
    summary["TimePerOp_us"] = (summary["TimeMean_ms"] * 1000.0) / num_ops_per_trial

    summary = summary.sort_values(["Key", "M", "Lazing", "HashFamily"]).reset_index(drop=True)
    summary.to_csv("results_summary.csv", index=False)

    print("\n====== Summary (runtime + error rate) ======\n")
    print(summary.to_string(index=False))

    summary["Setting"] = summary["HashFamily"].str.title() + " | opt=" + summary["Lazing"].astype(str)

    # Runtime bar chart
    g = sns.catplot(
        data=summary, x="M", y="TimeMean_ms", hue="Setting",
        col="Key", kind="bar", height=3, aspect=1.2, errorbar=None
    )
    g.set_axis_labels("Table size m", "Mean runtime (ms)")
    g.set_titles(col_template="Key = {col_name}")
    g.fig.subplots_adjust(top=0.85)
    g.fig.suptitle(f"Runtime — {num_ops_per_trial} ops/trial")
    g.fig.savefig("runtime_bar.png", bbox_inches="tight", dpi=200)
    plt.close(g.fig)  

    # Error rate bar chart
    g2 = sns.catplot(
        data=summary, x="M", y="IncorrectRate_%", hue="Setting",
        col="Key", kind="bar", height=3, aspect=1.2, errorbar=None
    )
    g2.set_axis_labels("Table size m", "Incorrect rate (%)")
    g2.set_titles(col_template="Key = {col_name}")
    g2.fig.subplots_adjust(top=0.85)
    g2.fig.suptitle(f"Incorrect Rate — {num_ops_per_trial} ops/trial")
    g2.fig.savefig("incorrect_rate_bar.png", bbox_inches="tight", dpi=200)
    plt.close(g2.fig)  

    return summary


# ----------------------------
# Driver
# ----------------------------
def experiments():
    recs = []
    combos = [(key_mode, m, lazing, hf)
              for key_mode in KEY_MODES
              for m in M_VALUES
              for lazing in LAZING_VALUES
              for hf in HASH_FAMILIES]

    total_trials = len(combos) * NUM_TRIALS
    done = 0

    for key_mode, m, lazing, hf_name in combos:
        for t in range(NUM_TRIALS):
            trial_seed = (hash((key_mode, m, lazing, hf_name, t)) & 0xFFFFFFFF)
            elapsed, incorrect = run_one_trial(key_mode, m, lazing, hf_name, trial_seed)

            recs.append({
                "Key": key_mode,
                "M": m,
                "Lazing": lazing,
                "HashFamily": hf_name,
                "Trial": t,
                "Runtime (ms)": elapsed * 1000.0,
                "IncorrectSearches": incorrect,
            })

            done += 1
            if done % 100 == 0:
                print(f"{done} of {total_trials} Trials Completed")

    df = pd.DataFrame(recs)
    summarize_and_plot(df, NUM_OPS)


def run():
    experiments()


if __name__ == "__main__":
    run()
