"""Phase 9: joint observed-volume/CV screening, not a stock-quantity model."""

from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import statistics

from .demand import file_hash

SEGMENTS = (
    'high volume / high volatility', 'high volume / low volatility',
    'low volume / high volatility', 'low volume / low volatility',
)
INTERPRETATIONS = {
    SEGMENTS[0]: 'Priority review: material observed volume plus above-portfolio-median relative variation. Validate local demand and availability before inventory changes.',
    SEGMENTS[1]: 'Material observed volume with lower relative variation; preserve reliable replenishment and monitor changes rather than infer low operational importance.',
    SEGMENTS[2]: 'Higher relative variation but lower observed volume; investigate selectively and avoid blanket buffer increases based on CV.',
    SEGMENTS[3]: 'Lower observed volume and relative variation; use proportionate routine review, subject to local service and shelf-life constraints.',
}


def segment_meals(meals, volume_threshold=None, cv_threshold=None):
    """Assign exactly one quadrant; reject undefined CV rather than label it low.

    Default medians use meals equally, including the median in the high side.
    Priorities first require BOTH high dimensions, then sort by volume, CV, ID.
    """
    rows = [dict(row) for row in meals]
    if not rows:
        raise ValueError('No meals to segment')
    if len({str(r['meal_id']) for r in rows}) != len(rows):
        raise ValueError('Duplicate meal IDs')
    for row in rows:
        if (row['cv'] is None or not math.isfinite(row['cv']) or row['cv'] < 0
                or not math.isfinite(row['orders']) or row['orders'] < 0):
            raise ValueError('Every meal needs finite nonnegative volume and defined CV')
    volume_cut = statistics.median(r['orders'] for r in rows) if volume_threshold is None else volume_threshold
    cv_cut = statistics.median(r['cv'] for r in rows) if cv_threshold is None else cv_threshold
    if any(not math.isfinite(x) or x < 0 for x in (volume_cut, cv_cut)):
        raise ValueError('Thresholds must be finite and nonnegative')
    for row in rows:
        high_volume, high_cv = row['orders'] >= volume_cut, row['cv'] >= cv_cut
        row['segment'] = f"{'high' if high_volume else 'low'} volume / {'high' if high_cv else 'low'} volatility"
        row['priority_review'] = high_volume and high_cv
        row['interpretation'] = INTERPRETATIONS[row['segment']]
    rows.sort(key=lambda r: int(r['meal_id']))
    priority = sorted((r for r in rows if r['priority_review']), key=lambda r: (-r['orders'], -r['cv'], int(r['meal_id'])))
    counts = Counter(r['segment'] for r in rows)
    total = sum(r['orders'] for r in rows)
    summaries = [{'segment': s, 'meals': counts[s], 'orders': sum(r['orders'] for r in rows if r['segment'] == s),
                  'observations': sum(r.get('observations', 0) for r in rows if r['segment'] == s),
                  'demand_share_pct': 100 * sum(r['orders'] for r in rows if r['segment'] == s) / total if total else None}
                 for s in SEGMENTS]
    return {'thresholds': {'volume_orders': volume_cut, 'cv': cv_cut,
                           'method': 'Unweighted median across all meals; high is >= threshold, low is < threshold',
                           'volume_definition': 'Total recorded orders across the historical window; not an imputed complete availability grid'},
            'meals': rows, 'segment_summary': summaries, 'priority_meal_ids': [str(r['meal_id']) for r in priority],
            'priority_rule': 'Both high-volume and high-CV required; within that group, order by volume descending, then CV descending, then numeric meal ID',
            'total_meals': len(rows), 'total_orders': total, 'missing_weeks_filled': 0}


def analyze_inventory(root):
    root = Path(root)
    source = root / 'data/processed/train_prepared.csv'
    p5 = json.loads((root / 'docs/phase5_audit.json').read_text())
    expected = p5['outputs']['train_prepared.csv']['sha256']
    if file_hash(source) != expected:
        raise ValueError('Phase 5 input hash mismatch')
    p7_path = root / 'data/processed/phase7/kpi_results.json'
    p7 = json.loads(p7_path.read_text())
    if p7['prepared_sha256'] != expected:
        raise ValueError('Phase 7 CV provenance mismatch')
    cv_rows = p7['volatility']
    if len({r['meal_id'] for r in cv_rows}) != len(cv_rows):
        raise ValueError('Duplicate Phase 7 CV records')
    volumes, observations = defaultdict(int), defaultdict(int)
    labels, centers, weeks = {}, defaultdict(set), defaultdict(set)
    count = total = 0
    with source.open(encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream):
            meal, orders = row['meal_id'], int(row['num_orders'])
            label = (row['category'], row['cuisine'])
            if meal in labels and labels[meal] != label:
                raise ValueError('Conflicting meal labels')
            labels[meal] = label; volumes[meal] += orders; observations[meal] += 1
            centers[meal].add(row['center_id']); weeks[meal].add(int(row['week']))
            count += 1; total += orders
    cv_by_id = {r['meal_id']: r for r in cv_rows}
    if set(volumes) != set(cv_by_id):
        raise ValueError('Meal volume/CV key coverage mismatch')
    if count != p7['observation_count'] or total != p7['total_orders']:
        raise ValueError('Observation/order conservation mismatch')
    meals = []
    for meal in volumes:
        previous = cv_by_id[meal]
        if previous['observations'] != observations[meal]:
            raise ValueError('Phase 7 CV sample coverage mismatch')
        meals.append({'meal_id': meal, 'meal_name': 'Not supplied', 'category': labels[meal][0], 'cuisine': labels[meal][1],
                      'orders': volumes[meal], 'cv': previous['cv'],
                      'mean_orders': previous['mean_orders'], 'sample_std_orders': previous['sample_std_orders'],
                      'observations': observations[meal], 'observed_centers': len(centers[meal]), 'observed_weeks': len(weeks[meal])})
    result = segment_meals(meals)
    result.update({'phase': 9, 'input_rows': count, 'prepared_sha256': expected, 'phase7_kpi_sha256': file_hash(p7_path),
                   'cv_definition': p7['cv_definition'], 'rows_removed': 0,
                   'metadata_combination': {'meals_before': len(volumes), 'cv_rows_before': len(cv_rows), 'meals_after': len(meals),
                                            'unmatched_volume_keys': 0, 'unmatched_cv_keys': 0, 'duplicate_expansion': 0,
                                            'orders_before': total, 'orders_after': result['total_orders']},
                   'limitations': 'CV pools observed center-meal-week rows (sample std/mean), mixing center differences and time variation; volume depends on coverage. No lead-time, stock, service-level, waste or shelf-life records support exact safety stock. Medians are relative screening thresholds, not validated risk cutoffs.'})
    if file_hash(source) != expected:
        raise ValueError('Prepared source changed')
    out = root / 'data/processed/phase9'; out.mkdir(exist_ok=True)
    (out / 'inventory_segments.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    with (out / 'meal_inventory_segments.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result['meals'][0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(result['meals'])
    return result


def inventory_figure(result):
    import matplotlib.pyplot as plt
    colors = ['#b33d3d', '#226c8a', '#b58421', '#71877b']
    fig, ax = plt.subplots(figsize=(12, 7), layout='constrained')
    for item, color in zip(result['segment_summary'], colors):
        rows = [r for r in result['meals'] if r['segment'] == item['segment']]
        ax.scatter([r['orders']/1e6 for r in rows], [r['cv'] for r in rows], s=70,
                   color=color, edgecolor='white', linewidth=.6,
                   label=f"{item['segment']} (n={item['meals']})")
    cuts = result['thresholds']
    ax.axvline(cuts['volume_orders']/1e6, color='#555555', ls='--', lw=1)
    ax.axhline(cuts['cv'], color='#555555', ls='--', lw=1)
    indexed = {str(r['meal_id']): r for r in result['meals']}
    for i, meal in enumerate(result['priority_meal_ids'][:5]):
        row = indexed[meal]
        ax.annotate(meal, (row['orders']/1e6, row['cv']), xytext=(7, 10 if i%2==0 else -16),
                    textcoords='offset points', fontsize=9, fontweight='bold')
    count = len(result['priority_meal_ids'])
    ax.set(title=f'{count} meals combine high observed volume with high relative variation',
           xlabel='Total observed demand across weeks 1–145 (millions of orders)',
           ylabel='Meal CV: sample std / mean of observed center-meal-week orders',
           xlim=(0, max(r['orders'] for r in result['meals'])/1e6*1.12), ylim=(0, max(r['cv'] for r in result['meals'])*1.15))
    ax.legend(loc='lower right', fontsize=8, framealpha=.95)
    ax.text(.02,.97,f"Median thresholds: {cuts['volume_orders']:,.0f} orders; CV {cuts['cv']:.4f}\nLabels: five largest-volume meals in the high/high segment",
            transform=ax.transAxes,va='top',fontsize=9)
    fig.supxlabel('Prioritize review using both dimensions. Missing observations remain absent; CV also reflects center differences.\nNo exact safety-stock quantity can be inferred without lead-time and inventory data.\nSource: validated Phase 5 historical observations and Phase 7 meal CVs; relative median-based screening.',fontsize=9)
    return fig
