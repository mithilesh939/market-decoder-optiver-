"""
convert_binance_csv.py

Converts Binance's historical monthly trades CSVs into our binary wire
format (33-byte TradeMsg records, per include/protocol.hpp), streaming
row-by-row so an 80M-row file never sits fully in memory.

CSV format (no header): trade_id, price, quantity, quote_qty,
timestamp_us, is_buyer_maker, is_best_match
"""
import csv
import struct
import sys
import time

TRADE_FMT = "<BQIqIQ"  # type, timestamp_ns, symbol_id, price, size, trade_id
MSG_TYPE_TRADE = 2
PRICE_SCALE = 1_000_000
QTY_SCALE = 1_000_000

assert struct.calcsize(TRADE_FMT) == 33, "TradeMsg format drifted from protocol.hpp"

PROGRESS_EVERY = 5_000_000


def convert(csv_path: str, bin_path: str, symbol_id: int = 1) -> int:
    start = time.time()
    row_count = 0
    skipped = 0

    with open(csv_path, "r", newline="") as csv_file, open(bin_path, "wb") as bin_file:
        reader = csv.reader(csv_file)
        for row in reader:
            try:
                trade_id = int(row[0])
                price = float(row[1])
                qty = float(row[2])
                timestamp_us = int(row[4])
            except (ValueError, IndexError):
                skipped += 1
                continue

            timestamp_ns = timestamp_us * 1000
            price_scaled = round(price * PRICE_SCALE)
            size_scaled = min(round(qty * QTY_SCALE), 2**32 - 1)

            bin_file.write(struct.pack(
                TRADE_FMT, MSG_TYPE_TRADE, timestamp_ns, symbol_id,
                price_scaled, size_scaled, trade_id,
            ))
            row_count += 1

            if row_count % PROGRESS_EVERY == 0:
                elapsed = time.time() - start
                rate = row_count / elapsed
                print(f"  {row_count:,} rows converted ({rate:,.0f} rows/sec, {elapsed:.1f}s elapsed)")

    elapsed = time.time() - start
    print(f"\nDone: {row_count:,} trades converted ({skipped} rows skipped) "
          f"in {elapsed:.1f}s ({row_count/elapsed:,.0f} rows/sec)")
    print(f"Output file: {bin_path} ({row_count * 33:,} bytes = {row_count * 33 / 1e9:.2f} GB, "
          f"33 bytes/record)")
    return row_count


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python3 convert_binance_csv.py <input.csv> <output.bin> [symbol_id]")
        sys.exit(1)
    csv_path = sys.argv[1]
    bin_path = sys.argv[2]
    symbol_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    convert(csv_path, bin_path, symbol_id)
