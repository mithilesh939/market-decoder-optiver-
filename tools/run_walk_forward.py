"""
Runs fixed-spread and Avellaneda-Stoikov backtests across all 12 real
months and compares them month by month -- checks if AS's edge holds up
or was a one-month fluke.

Usage: python3 tools/run_walk_forward.py <monthly_bins_dir> <output_csv>
"""
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.extract_trades_slice import extract_last_n
from strategy.backtest import run_backtest
from strategy.backtest_as import run_backtest_avellaneda_stoikov

SLICE_SIZE = 200_000

def run_one_month(bin_path: str, slice_dir: str) -> dict:
    month_name = os.path.basename(bin_path).replace(".bin", "")
    slice_path = os.path.join(slice_dir, f"{month_name}_slice.bin")

    if not os.path.exists(slice_path):
        extract_last_n(bin_path, slice_path, SLICE_SIZE)

    fixed = run_backtest(slice_path, half_spread=5.0, skew_per_unit_inventory=50.0, quote_size=0.01)
    as_result = run_backtest_avellaneda_stoikov(slice_path, gamma=0.0005, kappa=1.5, quote_size=0.01, vol_window=1000)

    return {
        "month": month_name,
        "fixed_fills": fixed.total_fills,
        "fixed_rejected": fixed.rejected_fills,
        "fixed_pnl": fixed.final_pnl(),
        "fixed_inventory": fixed.final_inventory(),
        "as_fills": as_result.total_fills,
        "as_rejected": as_result.rejected_fills,
        "as_pnl": as_result.final_pnl(),
        "as_inventory": as_result.final_inventory(),
    }

def main():
    if len(sys.argv) != 3:
        print("usage: python3 run_walk_forward.py <monthly_bins_dir> <output_csv>")
        sys.exit(1)

    bins_dir = sys.argv[1]
    output_csv = sys.argv[2]
    slice_dir = os.path.join(bins_dir, "walk_forward_slices")
    os.makedirs(slice_dir, exist_ok=True)

    bin_files = sorted(glob.glob(os.path.join(bins_dir, "*.bin")))
    bin_files = [f for f in bin_files if "slice" not in f]

    if not bin_files:
        print(f"no .bin files found in {bins_dir}")
        sys.exit(1)

    print(f"Found {len(bin_files)} months. Running fixed-spread and AS on each...\n")

    rows = []
    for bin_path in bin_files:
        print(f"--- {os.path.basename(bin_path)} ---")
        row = run_one_month(bin_path, slice_dir)
        rows.append(row)
        print(f"  fixed: fills={row['fixed_fills']} rejected={row['fixed_rejected']} "
              f"pnl=${row['fixed_pnl']:.2f} inventory={row['fixed_inventory']:.4f}")
        print(f"  as:    fills={row['as_fills']} rejected={row['as_rejected']} "
              f"pnl=${row['as_pnl']:.2f} inventory={row['as_inventory']:.4f}")
        print()

    with open(output_csv, "w") as f:
        headers = list(rows[0].keys())
        f.write(",".join(headers) + "\n")
        for row in rows:
            f.write(",".join(str(row[h]) for h in headers) + "\n")

    as_wins = sum(1 for r in rows if r["as_pnl"] > r["fixed_pnl"])
    print(f"AS beat fixed-spread on PnL in {as_wins}/{len(rows)} months")
    print(f"Fixed-spread total rejections: {sum(r['fixed_rejected'] for r in rows):,}")
    print(f"AS total rejections: {sum(r['as_rejected'] for r in rows):,}")
    print(f"\nWritten to {output_csv}")

if __name__ == "__main__":
    main()