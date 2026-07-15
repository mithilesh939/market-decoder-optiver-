from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


LATENCY_DIR = Path("results/latency")
OUTPUT_DIR = Path("results/latency_plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


for csv_file in LATENCY_DIR.glob("*_latency.csv"):

    df = pd.read_csv(csv_file)

    plt.figure(figsize=(8,5))

    plt.hist(df["latency_ns"], bins=80)

    plt.title(csv_file.stem.replace("_", " ").title())
    plt.xlabel("Latency (ns)")
    plt.ylabel("Samples")

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / f"{csv_file.stem}.png")

    plt.close()

print("Latency plots written to", OUTPUT_DIR)