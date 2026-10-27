"""Phase 7 descriptive KPIs. No promotion comparisons or statistical tests."""

from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
import statistics

from .demand import file_hash


def finite_decimal(value):
    """Return a finite decimal, or None for a missing/invalid numeric field."""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def discount_rate(base_price, checkout_price):
    """Unclamped signed rate; unavailable for nonpositive/invalid base or price."""
    base, checkout = finite_decimal(base_price), finite_decimal(checkout_price)
    if base is None or base <= 0 or checkout is None or checkout < 0:
        return None
    return (base - checkout) / base


def revenue_proxy(checkout_price, orders):
    """Price times units with decimal arithmetic; no currency/profit assumption."""
    checkout = finite_decimal(checkout_price)
    if checkout is None or checkout < 0:
        return None
    if isinstance(orders, bool) or int(orders) != orders or orders < 0:
        raise ValueError('Orders must be nonnegative integers')
    return checkout * orders


def promotion_share(flags):
    values = list(flags)
    if any(value not in (0, 1) for value in values):
        raise ValueError('Promotion flags must be binary 0/1')
    return sum(values) / len(values) if values else None


def coefficient_of_variation(values, min_mean=1e-12):
    """Sample std (ddof=1) / mean over observed demand; no zero imputation."""
    if not math.isfinite(min_mean) or min_mean < 0:
        raise ValueError('Minimum mean must be finite and nonnegative')
    values = list(values)
    if any(not math.isfinite(x) or x < 0 for x in values):
        raise ValueError('Demand must be finite and nonnegative')
    mean = statistics.mean(values) if values else None
    std = statistics.stdev(values) if len(values) >= 2 else None
    reason = ('no observations' if not values else 'fewer than two observations' if len(values) < 2
              else 'mean at or below minimum threshold' if mean <= min_mean else None)
    return {'observations': len(values), 'mean_orders': mean, 'sample_std_orders': std,
            'cv': std / mean if reason is None else None, 'unavailable_reason': reason}


def calculate_kpis(records):
    """Calculate complete totals and disclose denominator/coverage exclusions."""
    weeks, meals = defaultdict(int), defaultdict(list)
    meal_centers, meal_weeks = defaultdict(set), defaultdict(set)
    discounts, emails, homepages = [], [], []
    total_orders = count = negative = invalid_revenue = invalid_discount = 0
    valid_revenue = Decimal(0)
    excluded_revenue_orders = excluded_discount_orders = 0
    ids, logicals = set(), set()
    for row in records:
        orders, week = int(row['num_orders']), int(row['week'])
        if str(orders) != str(row['num_orders']) or orders < 0 or week <= 0:
            raise ValueError('Invalid order count or week')
        identity = str(row['id']); key = (week, str(row['center_id']), str(row['meal_id']))
        if identity in ids or key in logicals:
            raise ValueError('Duplicate observation')
        ids.add(identity); logicals.add(key)
        flags = [row['emailer_for_promotion'], row['homepage_featured']]
        if any(str(flag) not in {'0', '1'} for flag in flags):
            raise ValueError('Promotion flags must be binary 0/1')
        emails.append(int(flags[0])); homepages.append(int(flags[1]))
        count += 1; total_orders += orders; weeks[week] += orders
        meal = str(row['meal_id']); meals[meal].append(orders)
        meal_centers[meal].add(str(row['center_id'])); meal_weeks[meal].add(week)
        revenue = revenue_proxy(row['checkout_price'], orders)
        if revenue is None:
            invalid_revenue += 1; excluded_revenue_orders += orders
        else:
            valid_revenue += revenue
        discount = discount_rate(row['base_price'], row['checkout_price'])
        if discount is None:
            invalid_discount += 1; excluded_discount_orders += orders
        else:
            discounts.append(discount); negative += discount < 0
    volatility = [{'meal_id': meal, **coefficient_of_variation(values),
                   'observed_centers': len(meal_centers[meal]), 'observed_weeks': len(meal_weeks[meal])}
                  for meal, values in sorted(meals.items(), key=lambda pair: int(pair[0]))]
    mean_discount = sum(discounts, Decimal(0)) / len(discounts) if discounts else None
    result = {'observation_count': count, 'total_orders': total_orders,
              'observed_week_count': len(weeks),
              'average_weekly_demand': total_orders / len(weeks) if weeks else None,
              'revenue_proxy': str(valid_revenue) if count and invalid_revenue == 0 else None,
              'valid_row_revenue_proxy_subtotal': str(valid_revenue),
              'revenue_valid_rows': count - invalid_revenue, 'revenue_invalid_rows': invalid_revenue,
              'revenue_excluded_orders': excluded_revenue_orders,
              'discount_mean_rate': float(mean_discount) if mean_discount is not None else None,
              'discount_median_rate': float(statistics.median(discounts)) if discounts else None,
              'discount_min_rate': float(min(discounts)) if discounts else None,
              'discount_max_rate': float(max(discounts)) if discounts else None,
              'discount_valid_rows': len(discounts), 'discount_invalid_rows': invalid_discount,
              'discount_excluded_orders': excluded_discount_orders, 'negative_discount_rows': negative,
              'email_promotion_rows': sum(emails), 'email_promotion_share': promotion_share(emails),
              'homepage_feature_rows': sum(homepages), 'homepage_feature_share': promotion_share(homepages),
              'volatility': volatility, 'cv_definition': 'Sample std (ddof=1) / mean of observed center-meal-week num_orders, grouped by meal; unweighted rows; min_mean=1e-12 orders',
              'discount_definition': 'Unweighted mean of valid row (base_price-checkout_price)/base_price; includes negative rates',
              'share_definition': 'Fraction of observed rows flagged 1; not fraction of orders or weeks',
              'average_weekly_definition': 'Sum weekly recorded orders / count of observed global weeks; no missing weeks filled',
              'rows_removed': 0, 'values_clamped': 0, 'weeks_imputed': 0}
    if sum(item['observations'] for item in volatility) != count:
        raise ValueError('Volatility group coverage mismatch')
    return result


def calculate_prepared_kpis(root):
    root = Path(root)
    audit = json.loads((root / 'docs/phase5_audit.json').read_text())
    source = root / 'data/processed/train_prepared.csv'
    before = file_hash(source)
    if before != audit['outputs']['train_prepared.csv']['sha256']:
        raise ValueError('Prepared source differs from Phase 5')
    with source.open(encoding='utf-8', newline='') as stream:
        result = calculate_kpis(csv.DictReader(stream))
    if result['observation_count'] != audit['prepared_audit']['rows'] or result['total_orders'] != audit['prepared_audit']['num_orders_total']:
        raise ValueError('KPI conservation mismatch')
    if file_hash(source) != before:
        raise ValueError('Source changed during calculation')
    result['prepared_sha256'] = before
    return result


def kpi_table(result):
    return [
        {'metric': 'Total orders', 'value': result['total_orders'], 'unit': 'orders', 'denominator': 'all recorded observations'},
        {'metric': 'Average weekly demand', 'value': result['average_weekly_demand'], 'unit': 'orders per observed global week', 'denominator': result['observed_week_count']},
        {'metric': 'Revenue proxy (not profit)', 'value': result['revenue_proxy'], 'unit': 'unspecified price units', 'denominator': f"{result['revenue_valid_rows']} valid rows; {result['revenue_invalid_rows']} invalid"},
        {'metric': 'Mean signed discount rate', 'value': result['discount_mean_rate'], 'unit': 'fraction', 'denominator': result['discount_valid_rows']},
        {'metric': 'Email-promotion share', 'value': result['email_promotion_share'], 'unit': 'fraction of observations', 'denominator': result['observation_count']},
        {'metric': 'Homepage-feature share', 'value': result['homepage_feature_share'], 'unit': 'fraction of observations', 'denominator': result['observation_count']},
    ]


def write_kpi_outputs(result, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    (output / 'kpi_results.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    for name, rows in [('kpi_summary.csv', kpi_table(result)), ('meal_volatility.csv', result['volatility'])]:
        with (output / name).open('w', encoding='utf-8', newline='') as stream:
            keys = list(rows[0]) if rows else ['meal_id','observations','mean_orders','sample_std_orders','cv','unavailable_reason','observed_centers','observed_weeks']
            writer = csv.DictWriter(stream, fieldnames=keys, lineterminator='\n')
            writer.writeheader(); writer.writerows(rows)
