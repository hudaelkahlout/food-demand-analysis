"""Exploratory Phase 6 figures; no client-report or final-figure exports."""

import matplotlib.pyplot as plt

COLOR = '#246b85'


def weekly_figure(result):
    rows = result['weekly']; peak = result['weekly_summary']['peak']
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, layout='constrained')
    axes[0].plot([r['week'] for r in rows], [r['orders'] / 1e6 for r in rows], color=COLOR)
    axes[0].set(title=f"Observed demand peaked in week {peak['week']} at {peak['orders']:,} orders", ylabel='Observed orders (millions)')
    valid = [r for r in rows if r['change_pct'] is not None]
    axes[1].bar([r['week'] for r in valid], [r['change_pct'] for r in valid], color=COLOR)
    axes[1].axhline(0, color='black', lw=.6)
    axes[1].set(xlabel='Sequential week index (no calendar dates)', ylabel='Week-to-week change (%)')
    fig.supxlabel('Exploratory: observed orders only; assortment and observation coverage vary. No absent records were filled.', fontsize=9)
    return fig


def pareto_figure(result, key, label):
    values = result[key]; rows = values['ranking']; n = values['threshold_count']
    fig, ax = plt.subplots(figsize=(13, 6), layout='constrained')
    ax.bar(range(len(rows)), [r['orders'] / 1e6 for r in rows], color=[COLOR if i < n else '#c4cdd0' for i in range(len(rows))])
    ax.set_xticks(range(len(rows)), [r['key'] for r in rows], rotation=60 if key == 'categories' else 90, ha='right', fontsize=8)
    ax.set(ylabel='Observed orders (millions)', xlabel=label,
           title=f"{n} {label.lower()} account for {values['selected_share_pct']:.2f}% of observed demand")
    right = ax.twinx(); right.plot(range(len(rows)), [r['cumulative_pct'] for r in rows], color='#c67626', marker='.', label='Cumulative share')
    right.axhline(80, color='#c67626', ls='--', lw=.8); right.set(ylabel='Cumulative demand (%)', ylim=(0, 105))
    fig.supxlabel('Exploratory: smallest ranked prefix reaching 80%, including the crossing group. Blue bars show that prefix.', fontsize=9)
    return fig


def center_figure(result):
    rows = result['centers'][:10]
    fig, ax = plt.subplots(figsize=(11, 6), layout='constrained')
    ax.barh([r['center_id'] for r in rows][::-1], [r['average_observed_week_orders'] for r in rows][::-1], color=COLOR)
    ax.set(xlabel='Orders per observed center-week', ylabel='Coded center ID',
           title=f"Center {rows[0]['center_id']} leads demand; bars show weekly averages for the top 10 by total")
    fig.supxlabel('Exploratory: volumes reflect observed assortment, area, and exposure; this is not an efficiency ranking.', fontsize=9)
    return fig


def type_figure(result):
    rows = result['center_types']; leader = max(rows, key=lambda r: r['orders_per_observed_center_week'])
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    axes[0].bar([r['center_type'] for r in rows], [r['orders'] / 1e6 for r in rows], color=COLOR)
    axes[0].set(title='Total volume reflects unequal center counts', ylabel='Observed orders (millions)')
    axes[1].bar([r['center_type'] for r in rows], [r['orders_per_observed_center_week'] for r in rows], color=COLOR)
    axes[1].set(title=f"{leader['center_type']} leads per observed center-week", ylabel='Orders per observed center-week')
    fig.supxlabel('Exploratory: area and assortment differ across types; no causal center-type effect is estimated.', fontsize=9)
    return fig
