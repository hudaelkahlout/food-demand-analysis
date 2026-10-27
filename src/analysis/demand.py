"""Reproducible Phase 6 aggregates; no imputation, inference or promotion analysis."""

from collections import defaultdict
import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import statistics


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def weekly_changes(totals, counts=None):
    """Compare consecutive observed weeks only; never fill absent weeks with zero."""
    result, previous = [], None
    for week, total in sorted(totals.items()):
        adjacent = previous is not None and week == previous['week'] + 1
        delta = total - previous['orders'] if adjacent else None
        percent = 100 * delta / previous['orders'] if adjacent and previous['orders'] else None
        result.append({'week': week, 'orders': total, 'observations': counts.get(week) if counts else None,
                       'change_orders': delta, 'change_pct': percent,
                       'comparison': 'consecutive week' if adjacent else 'unavailable: first or nonconsecutive week'})
        previous = result[-1]
    return result


def concentration(totals, target=.8):
    """Smallest descending prefix reaching target, including the crossing group.

    Ties use lexical key order. Ratios use the full observed demand denominator.
    """
    if not 0 < target <= 1 or not totals or any(v < 0 for v in totals.values()) or sum(totals.values()) <= 0:
        raise ValueError('Concentration needs nonnegative demand, a positive total, and target in (0,1]')
    denominator, cumulative = sum(totals.values()), 0
    rows, selected_count = [], None
    threshold = Fraction(str(target))
    for index, (key, orders) in enumerate(sorted(totals.items(), key=lambda item: (-item[1], str(item[0]))), 1):
        cumulative += orders
        rows.append({'key': key, 'orders': orders, 'share_pct': 100 * orders / denominator,
                     'cumulative_orders': cumulative, 'cumulative_pct': 100 * cumulative / denominator})
        if selected_count is None and Fraction(cumulative, denominator) >= threshold:
            selected_count = index
    selected = rows[:selected_count]
    return {'ranking': rows, 'total_orders': denominator, 'target_pct': 100 * target,
            'threshold_count': selected_count, 'selected_keys': [r['key'] for r in selected],
            'selected_orders': selected[-1]['cumulative_orders'], 'selected_share_pct': selected[-1]['cumulative_pct'],
            'previous_share_pct': rows[selected_count - 2]['cumulative_pct'] if selected_count > 1 else 0,
            'selection_accounting': {'groups_before': len(rows), 'groups_selected': selected_count,
                                     'groups_remaining': len(rows) - selected_count,
                                     'orders_before': denominator, 'orders_selected': selected[-1]['cumulative_orders'],
                                     'orders_remaining': denominator - selected[-1]['cumulative_orders']},
            'tie_policy': 'Descending orders; lexical group key breaks ties; include threshold-crossing group'}


def analyze_records(records):
    """Aggregate actual observations, retaining unequal observation coverage."""
    week_totals, week_counts = defaultdict(int), defaultdict(int)
    categories, meals = defaultdict(int), defaultdict(int)
    center_week = defaultdict(int)
    center_info, meal_info = {}, {}
    seen_ids, seen_logical = set(), set()
    count = total = 0
    for row in records:
        week, orders = int(row['week']), int(row['num_orders'])
        if week < 1 or orders < 0:
            raise ValueError('Invalid week or negative orders')
        center, meal = str(row['center_id']), str(row['meal_id'])
        logical = (week, center, meal)
        if row['id'] in seen_ids or logical in seen_logical:
            raise ValueError('Duplicate demand identifier or logical key')
        seen_ids.add(row['id']); seen_logical.add(logical)
        info = (row['center_type'], float(row['op_area']))
        if not info[0] or not math.isfinite(info[1]) or not info[1] > 0:
            raise ValueError('Missing center type or nonpositive operating area')
        if center in center_info and center_info[center] != info:
            raise ValueError('Conflicting center attributes')
        if meal in meal_info and meal_info[meal] != row['category']:
            raise ValueError('Conflicting meal category')
        if not row['category']:
            raise ValueError('Missing category')
        center_info[center], meal_info[meal] = info, row['category']
        week_totals[week] += orders; week_counts[week] += 1
        categories[row['category']] += orders; meals[meal] += orders
        center_week[(center, week)] += orders
        count += 1; total += orders
    if not count:
        raise ValueError('No observed demand records')
    weekly = weekly_changes(week_totals, week_counts)
    centers = []
    for center, (kind, area) in center_info.items():
        observed = [value for (c, week), value in center_week.items() if c == center]
        centers.append({'center_id': center, 'center_type': kind, 'op_area': area,
                        'orders': sum(observed), 'observed_weeks': len(observed),
                        'missing_global_weeks': len(week_totals) - len(observed),
                        'average_observed_week_orders': sum(observed) / len(observed)})
    centers.sort(key=lambda r: (-r['orders'], r['center_id']))
    types = []
    for kind in sorted({r['center_type'] for r in centers}):
        subset = [r for r in centers if r['center_type'] == kind]
        orders = sum(r['orders'] for r in subset)
        observed = sum(r['observed_weeks'] for r in subset)
        types.append({'center_type': kind, 'centers': len(subset), 'orders': orders,
                      'observed_center_weeks': observed,
                      'orders_per_observed_center_week': orders / observed,
                      'median_center_weekly_average': statistics.median(r['average_observed_week_orders'] for r in subset),
                      'op_area_min': min(r['op_area'] for r in subset),
                      'op_area_median': statistics.median(r['op_area'] for r in subset),
                      'op_area_max': max(r['op_area'] for r in subset)})
    category_result, meal_result = concentration(categories), concentration(meals)
    for row in meal_result['ranking']:
        row['category'] = meal_info[row['key']]
    changes = [r for r in weekly if r['change_pct'] is not None]
    window = min(10, len(weekly))
    summary = {'first': weekly[0], 'last': weekly[-1],
               'first_to_last_pct': 100 * (weekly[-1]['orders'] - weekly[0]['orders']) / weekly[0]['orders'] if weekly[0]['orders'] else None,
               'peak': max(weekly, key=lambda r: r['orders']), 'trough': min(weekly, key=lambda r: r['orders']),
               'largest_pct_increase': max(changes, key=lambda r: r['change_pct']) if changes else None,
               'largest_pct_decrease': min(changes, key=lambda r: r['change_pct']) if changes else None,
               'largest_absolute_increase': max(changes, key=lambda r: r['change_orders']) if changes else None,
               'largest_absolute_decrease': min(changes, key=lambda r: r['change_orders']) if changes else None,
               'comparison_block_observed_weeks': window,
               'first_block_average': sum(r['orders'] for r in weekly[:window]) / window,
               'last_block_average': sum(r['orders'] for r in weekly[-window:]) / window,
               'largest_five_absolute_pct_changes': sorted(changes, key=lambda r: (-abs(r['change_pct']), r['week']))[:5]}
    partitions = {'weekly': sum(r['orders'] for r in weekly), 'category': sum(categories.values()),
                  'meal': sum(meals.values()), 'center': sum(r['orders'] for r in centers),
                  'center_type': sum(r['orders'] for r in types)}
    if any(value != total for value in partitions.values()):
        raise ValueError('Aggregation conservation failed')
    return {'input_rows': count, 'input_orders': total, 'observed_weeks': len(weekly),
            'globally_missing_weeks': sorted(set(range(min(week_totals), max(week_totals) + 1)) - week_totals.keys()),
            'weekly': weekly, 'weekly_summary': summary, 'categories': category_result, 'meals': meal_result,
            'centers': centers, 'center_types': types, 'partition_order_totals': partitions,
            'rows_removed': 0, 'missing_weeks_filled': 0,
            'center_week_denominator': 'Only recorded center-weeks, aggregated across observed meals; no absent meal-week zeros inferred'}


def analyze_prepared(root):
    root = Path(root)
    audit = json.loads((root / 'docs/phase5_audit.json').read_text())
    path = root / 'data/processed/train_prepared.csv'
    before = file_hash(path)
    if before != audit['outputs']['train_prepared.csv']['sha256']:
        raise ValueError('Prepared file differs from validated Phase 5 output')
    with path.open(encoding='utf-8', newline='') as stream:
        result = analyze_records(csv.DictReader(stream))
    if result['input_rows'] != audit['prepared_audit']['rows'] or result['input_orders'] != audit['prepared_audit']['num_orders_total']:
        raise ValueError('Phase 5 conservation mismatch')
    if file_hash(path) != before:
        raise ValueError('Prepared input changed during analysis')
    result['prepared_sha256'] = before
    return result
