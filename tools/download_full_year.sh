#!/usr/bin/env bash
# download_full_year.sh
#
# Downloads, verifies, unzips, and converts all 12 months of 2025
# BTCUSDT trade history from Binance's public data archive -- straight
# into WSL, no Windows Downloads folder in the loop this time.
set -uo pipefail  # NOT -e: one bad month shouldn't kill the whole batch

BASE_URL="https://data.binance.vision/data/spot/monthly/trades/BTCUSDT"
DATA_DIR="datasets/binance/BTCUSDT/2025"
BIN_DIR="tools/monthly_bins"
mkdir -p "$DATA_DIR" "$BIN_DIR"

SUCCESS=()
FAILED=()

for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
    fname="BTCUSDT-trades-2025-${month}"
    zip_path="${DATA_DIR}/${fname}.zip"
    csv_path="${DATA_DIR}/${fname}.csv"
    bin_path="${BIN_DIR}/${fname}.bin"

    if [[ -f "$bin_path" ]]; then
        echo "=== $fname: already converted, skipping ==="
        SUCCESS+=("$fname")
        continue
    fi

    echo "=== $fname: downloading ==="
    if ! curl -sf "${BASE_URL}/${fname}.zip" -o "$zip_path"; then
        echo "!!! $fname: download FAILED (month may not exist yet, or network issue)"
        FAILED+=("$fname (download)")
        continue
    fi
    curl -sf "${BASE_URL}/${fname}.zip.CHECKSUM" -o "${zip_path}.CHECKSUM" || true

    echo "=== $fname: verifying checksum ==="
    if [[ -f "${zip_path}.CHECKSUM" ]]; then
        if ! (cd "$DATA_DIR" && sha256sum -c "${fname}.zip.CHECKSUM"); then
            echo "!!! $fname: CHECKSUM MISMATCH -- corrupted download, skipping"
            FAILED+=("$fname (checksum)")
            rm -f "$zip_path"
            continue
        fi
    fi

    echo "=== $fname: unzipping ==="
    if ! unzip -o -q "$zip_path" -d "$DATA_DIR"; then
        echo "!!! $fname: unzip FAILED"
        FAILED+=("$fname (unzip)")
        continue
    fi

    echo "=== $fname: converting to binary ==="
    if python3 tools/convert_binance_csv.py "$csv_path" "$bin_path"; then
        SUCCESS+=("$fname")
        # Raw CSV is regenerable from the zip -- delete it to save space,
        # but keep the zip (small, and re-unzipping is instant vs re-downloading).
        rm -f "$csv_path"
    else
        echo "!!! $fname: conversion FAILED"
        FAILED+=("$fname (conversion)")
    fi
    echo ""
done

echo ""
echo "=========================================="
echo "SUCCESS (${#SUCCESS[@]}/12): ${SUCCESS[*]}"
echo "FAILED  (${#FAILED[@]}/12): ${FAILED[*]}"
echo "=========================================="
echo "Converted files are in: $BIN_DIR"
ls -lh "$BIN_DIR"
