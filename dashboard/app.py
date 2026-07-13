"""
app.py -- real-data dashboard. Every number traces to a real tool:
./benchmark, ./bench_scale, RiskEngine, run_backtest. Nothing here is
fabricated.

Data files are configurable via DASHBOARD_BENCHMARK_FILE, DASHBOARD_SCALE_FILE,
and DASHBOARD_BACKTEST_FILE environment variables.

IMPORTANT: the charts show "NO DATA -- click Refresh" on page load, by
design -- that's the placeholder state, not a bug. Click the Refresh
button to actually run the real tools and populate them. If something
fails, the status-text banner at the top will show the full error --
read that first before assuming the graphs are broken.

Run: python -m dashboard.app
"""
import os
import traceback
import struct

import dash
from dash import dcc, html, Input, Output

from dashboard.style import (COLORS, CONTAINER_STYLE, PANEL_STYLE, CARD_STYLE,
                              LABEL_STYLE, VALUE_STYLE, PANEL_TITLE_STYLE)
from dashboard import charts
from dashboard.data_pipeline import (run_decoder_benchmark, run_scale_test,
                                      run_risk_engine_demo, run_market_maker_backtest)

BENCHMARK_FILE = os.environ.get("DASHBOARD_BENCHMARK_FILE", "tools/monthly_bins/BTCUSDT-trades-2025-06.bin")
SCALE_FILE = os.environ.get("DASHBOARD_SCALE_FILE", BENCHMARK_FILE)
BACKTEST_FILE = os.environ.get("DASHBOARD_BACKTEST_FILE", BENCHMARK_FILE)

app = dash.Dash(__name__, title="Real-Data Trading Systems Dashboard")


def panel(title, children):
    return html.Div(style=PANEL_STYLE, children=[html.Div(title, style=PANEL_TITLE_STYLE), *children])


def metric_card(label, value, color=None):
    style = dict(VALUE_STYLE)
    if color:
        style["color"] = color
    return html.Div(style=CARD_STYLE, children=[html.Div(label, style=LABEL_STYLE), html.Div(value, style=style)])


app.layout = html.Div(style=CONTAINER_STYLE, children=[
    html.Div(style={**PANEL_STYLE, "borderLeft": f"4px solid {COLORS['teal']}"}, children=[
        html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap", "gap": "12px"}, children=[
            html.Div([
                html.H1("REAL-DATA TRADING SYSTEMS DASHBOARD", style={"fontSize": "18px", "margin": 0, "fontFamily": "JetBrains Mono, monospace"}),
                html.Div([
                    html.Div(f"Benchmark file: {BENCHMARK_FILE}", style={"fontSize": "11px", "color": COLORS["text_secondary"], "fontFamily": "JetBrains Mono, monospace"}),
                    html.Div(f"Scale-test file: {SCALE_FILE}", style={"fontSize": "11px", "color": COLORS["text_secondary"], "fontFamily": "JetBrains Mono, monospace"}),
                    html.Div(f"Backtest file: {BACKTEST_FILE}", style={"fontSize": "11px", "color": COLORS["text_secondary"], "fontFamily": "JetBrains Mono, monospace"}),
                ], style={"marginTop": "4px"}),
            ]),
            html.Button("↻ REFRESH (re-run all real tools)", id="refresh-button", n_clicks=0,
                        style={"background": COLORS["teal"], "color": "#000", "fontWeight": "bold",
                               "border": "none", "padding": "10px 16px", "borderRadius": "4px", "cursor": "pointer"}),
        ]),
        html.Div("Click Refresh above to run the real pipeline. Status appears here:", style={"fontSize": "10px", "color": COLORS["text_muted"], "marginTop": "10px", "fontFamily": "JetBrains Mono, monospace"}),
        html.Div(id="status-text", style={"fontSize": "11px", "color": COLORS["amber"], "marginTop": "4px", "fontFamily": "JetBrains Mono, monospace"}),
    ]),

    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
        panel("Decoder Benchmark (./benchmark)", [
            html.Div(id="benchmark-cards", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px", "marginBottom": "12px"}),
            dcc.Graph(id="benchmark-chart", figure=charts.empty_figure("DECODE LATENCY"), config={"displayModeBar": False}),
        ]),
        panel("Memory / Scale Test (./bench_scale)", [
            html.Div(id="scale-cards", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px", "marginBottom": "12px"}),
            dcc.Graph(id="scale-chart", figure=charts.empty_figure("MEMORY OVER TIME"), config={"displayModeBar": False}),
        ]),
    ]),

    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
        panel("Risk Engine (real RiskEngine, real rules)", [
            html.Div(id="risk-cards", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px", "marginBottom": "12px"}),
            dcc.Graph(id="risk-chart", figure=charts.empty_figure("RISK DECISIONS"), config={"displayModeBar": False}),
        ]),
        panel("Market Maker Backtest (real trades, real fills)", [
            html.Div(id="backtest-cards", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px", "marginBottom": "12px"}),
        ]),
    ]),

    panel("Market Maker PnL & Inventory (real backtest)", [
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
            dcc.Graph(id="pnl-chart", figure=charts.empty_figure("PnL"), config={"displayModeBar": False}),
            dcc.Graph(id="inventory-chart", figure=charts.empty_figure("Inventory"), config={"displayModeBar": False}),
        ]),
    ]),

    html.Div(style={"fontSize": "10px", "color": COLORS["text_muted"], "marginTop": "8px", "fontFamily": "JetBrains Mono, monospace"}, children=[
        "Reproducibility: every number above comes from ./benchmark, ./bench_scale, ",
        "risk.engine.RiskEngine, and strategy.backtest.run_backtest -- run any directly ",
        "in your terminal against the same data file to verify.",
    ]),
])


@app.callback(
    Output("status-text", "children"),
    Output("benchmark-cards", "children"), Output("benchmark-chart", "figure"),
    Output("scale-cards", "children"), Output("scale-chart", "figure"),
    Output("risk-cards", "children"), Output("risk-chart", "figure"),
    Output("backtest-cards", "children"),
    Output("pnl-chart", "figure"), Output("inventory-chart", "figure"),
    Input("refresh-button", "n_clicks"),
)
def refresh_all(n_clicks):
    if n_clicks == 0:
        empty = charts.empty_figure("NO DATA")
        return "Waiting for you to click Refresh...", [], empty, [], empty, [], empty, [], empty, empty

    try:
        missing = [f for f in (BENCHMARK_FILE, SCALE_FILE, BACKTEST_FILE) if not os.path.exists(f)]
        if missing:
            err = f"File(s) not found: {missing}"
            empty = charts.empty_figure("NO DATA")
            return err, [], empty, [], empty, [], empty, [], empty, empty

        bench = run_decoder_benchmark(BENCHMARK_FILE)
        bench_cards = [
            metric_card("Speedup", f"{bench.speedup:.2f}x", COLORS["teal"]),
            metric_card("Checksums Match", "YES" if bench.checksums_match else "NO — BUG",
                        COLORS["teal"] if bench.checksums_match else COLORS["red"]),
            metric_card("MmapDecoder Throughput", f"{bench.mmap_msgs_per_sec/1e6:.1f}M msgs/sec"),
            metric_card("Messages Decoded", f"{bench.message_count:,}"),
        ]
        bench_fig = charts.build_benchmark_bar(bench.naive_ns_per_msg, bench.mmap_ns_per_msg)

        scale = run_scale_test(SCALE_FILE)
        scale_cards = [
            metric_card("File Size", f"{scale.file_size_mb:,.0f} MB"),
            metric_card("Peak RSS", f"{scale.peak_rss_mb:,.0f} MB"),
            metric_card("Decode Time", f"{scale.decode_ms:,.0f} ms"),
            metric_card("Messages", f"{scale.message_count:,}"),
        ]
        scale_fig = charts.build_rss_curve(scale.rss_curve_ms, scale.rss_curve_mb)

        with open(BENCHMARK_FILE, "rb") as f:
            f.seek(-33, os.SEEK_END)
            last_record = f.read(33)
        _, _, _, last_price_scaled, _, _ = struct.unpack("<BQIqIQ", last_record)
        last_price = last_price_scaled / 1_000_000

        risk = run_risk_engine_demo(current_price=last_price)
        risk_cards = [
            metric_card("Reference Price (real last trade)", f"${last_price:,.2f}"),
            metric_card("Accepted / Rejected", f"{risk.accepted} / {sum(risk.rejected_by_rule.values())}"),
        ]
        risk_fig = charts.build_risk_pie(risk.rejected_by_rule, risk.accepted)

        backtest = run_market_maker_backtest(BACKTEST_FILE)
        backtest_cards = [
            metric_card("Total Fills", f"{backtest.total_fills:,}"),
            metric_card("Rejected Fills", f"{backtest.rejected_fills:,}"),
            metric_card("Final PnL", f"${backtest.final_pnl():,.2f}",
                        COLORS["teal"] if backtest.final_pnl() >= 0 else COLORS["red"]),
            metric_card("Final Inventory", f"{backtest.final_inventory():.5f} BTC"),
        ]
        ticks = [p.tick for p in backtest.points]
        pnl_fig = charts.build_pnl_curve(ticks, [p.mark_to_market_pnl for p in backtest.points])
        inv_fig = charts.build_inventory_curve(ticks, [p.inventory for p in backtest.points])

        status = f"✓ Refreshed successfully: {bench.message_count:,} messages processed, all tools ran without error."
        return status, bench_cards, bench_fig, scale_cards, scale_fig, risk_cards, risk_fig, backtest_cards, pnl_fig, inv_fig

    except Exception:
        err_text = traceback.format_exc()
        print(err_text)
        empty = charts.empty_figure("ERROR — see status text above")
        return html.Pre(err_text, style={"color": COLORS["red"], "fontSize": "10px", "whiteSpace": "pre-wrap"}), [], empty, [], empty, [], empty, [], empty, empty


if __name__ == "__main__":
    app.run(debug=True, port=8050)
