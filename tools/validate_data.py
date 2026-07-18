"""
validate_data.py

Sanity-checks the loaded trades data: expected date coverage, no gaps,
row counts per month, and basic distribution checks. Run this once
after loading and paste the output into your README/portfolio as
concrete evidence of data integrity.

Usage: python3 validate_data.py
"""
import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, dbname="quant",
                         user="quant", password="quant_dev_password")

checks = [
    ("Date range", "SELECT min(bucket), max(bucket) FROM trades_ohlcv_1d;"),
    ("Days covered", "SELECT count(*) FROM trades_ohlcv_1d;"),
    ("Expected days (Jan 1 - Jun 30 2025)",
     "SELECT (DATE '2025-06-30' - DATE '2025-01-01' + 1);"),
    ("Missing days", """
        SELECT count(*) FROM generate_series(
            '2025-01-01'::date, '2025-06-30'::date, '1 day') d
        WHERE d NOT IN (SELECT bucket::date FROM trades_ohlcv_1d);
    """),
    ("Rows per month", """
        SELECT date_trunc('month', bucket)::date AS month, sum(trade_count)
        FROM trades_ohlcv_1d GROUP BY 1 ORDER BY 1;
    """),
    ("Any zero/negative prices", "SELECT count(*) FROM trades WHERE price <= 0;"),
    ("Any zero/negative qty", "SELECT count(*) FROM trades WHERE qty <= 0;"),
    ("Total trades (from aggregate)", "SELECT sum(trade_count) FROM trades_ohlcv_1d;"),
]

with conn.cursor() as cur:
    for label, sql in checks:
        cur.execute(sql)
        rows = cur.fetchall()
        print(f"\n{label}:")
        for row in rows:
            print(f"  {row}")

conn.close()
