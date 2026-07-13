"""charts.py -- every function takes REAL computed data as arguments."""
import plotly.graph_objects as go
from dashboard.style import COLORS


def _base_layout(fig: go.Figure, title: str, block_size: int = 260):
    fig.update_layout(
        height=block_size, margin=dict(l=40, r=20, t=36, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=11, color=COLORS["text_secondary"]),
        title=dict(text=title, font=dict(size=12, color=COLORS["text_primary"])),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLORS["border"], zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"], zeroline=False)
    return fig


def build_benchmark_bar(naive_ns: float, mmap_ns: float) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=["Naive Decoder", "MmapDecoder"], y=[naive_ns, mmap_ns],
        marker_color=[COLORS["red"], COLORS["teal"]],
        text=[f"{naive_ns:.2f} ns/msg", f"{mmap_ns:.2f} ns/msg"], textposition="outside",
    ))
    return _base_layout(fig, "DECODE LATENCY (ns/msg, lower is better)")


def build_rss_curve(ms: list, mb: list) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=ms, y=mb, mode="lines", line=dict(color=COLORS["amber"], width=2),
        fill="tozeroy", fillcolor="rgba(255,176,0,0.08)",
    ))
    fig.update_xaxes(title_text="elapsed (ms)")
    fig.update_yaxes(title_text="RSS (MB)")
    return _base_layout(fig, "MEMORY (RSS) OVER TIME DURING DECODE")


def build_risk_pie(rejected_by_rule: dict, accepted: int) -> go.Figure:
    labels = ["Accepted"] + list(rejected_by_rule.keys())
    values = [accepted] + list(rejected_by_rule.values())
    colors = [COLORS["teal"]] + [COLORS["red"], COLORS["amber"], "#FF8C42"][: len(rejected_by_rule)]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                            marker=dict(colors=colors), textinfo="label+value"))
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15))
    return _base_layout(fig, "RISK ENGINE DECISIONS (this run)")


def build_pnl_curve(ticks: list, pnl: list) -> go.Figure:
    fig = go.Figure(go.Scatter(x=ticks, y=pnl, mode="lines", line=dict(color=COLORS["teal"], width=2)))
    fig.update_xaxes(title_text="tick")
    fig.update_yaxes(title_text="mark-to-market PnL ($)")
    return _base_layout(fig, "MARKET MAKER PnL (real backtest, real data)")


def build_inventory_curve(ticks: list, inventory: list) -> go.Figure:
    fig = go.Figure(go.Scatter(x=ticks, y=inventory, mode="lines", line=dict(color=COLORS["amber"], width=2)))
    fig.update_xaxes(title_text="tick")
    fig.update_yaxes(title_text="inventory (BTC)")
    return _base_layout(fig, "MARKET MAKER INVENTORY (real backtest, real data)")


def empty_figure(title: str, block_size: int = 260) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text="NO DATA -- click Refresh", xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False, font=dict(size=11, color=COLORS["text_muted"]))
    return _base_layout(fig, title, block_size)
