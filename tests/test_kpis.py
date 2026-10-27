"""Deterministic formula, denominator and coverage tests for Phase 7."""

from decimal import Decimal
import math
import unittest

from src.analysis.kpis import (calculate_kpis, coefficient_of_variation,
                               discount_rate, promotion_share, revenue_proxy)


def row(identity, week=1, meal='1', orders=2, checkout='10.00', base='20.00', email='0', homepage='0'):
    return dict(id=str(identity), week=str(week), center_id=str(identity), meal_id=meal,
                num_orders=str(orders), checkout_price=checkout, base_price=base,
                emailer_for_promotion=email, homepage_featured=homepage)


class KpiTests(unittest.TestCase):
    def test_decimal_revenue_preserves_cents(self):
        self.assertEqual(revenue_proxy('0.10', 3), Decimal('0.30'))
        self.assertEqual(revenue_proxy('0', 3), 0)
        with self.assertRaises(ValueError):
            revenue_proxy('1', 1.5)

    def test_discount_signed_and_not_clamped(self):
        self.assertEqual(discount_rate('100', '80'), Decimal('.2'))
        self.assertEqual(discount_rate('100', '110'), Decimal('-.1'))
        self.assertEqual(discount_rate('100', '100'), 0)

    def test_invalid_denominators_and_nonfinite_prices(self):
        for base in ['0', '-10', 'NaN', 'Infinity', '', None]:
            self.assertIsNone(discount_rate(base, '10'))
        for checkout in ['NaN', 'Infinity', '-1', '', None]:
            self.assertIsNone(discount_rate('10', checkout))
            self.assertIsNone(revenue_proxy(checkout, 2))

    def test_weekly_average_uses_week_totals_not_row_mean(self):
        r = calculate_kpis([row(1, 1, orders=10), row(2, 1, orders=20), row(3, 3, orders=50)])
        self.assertEqual(r['total_orders'], 80)
        self.assertEqual(r['observed_week_count'], 2)
        self.assertEqual(r['average_weekly_demand'], 40)
        self.assertEqual(r['weeks_imputed'], 0)

    def test_shares_use_observations_not_orders(self):
        r = calculate_kpis([row(1, orders=1000, email='1'), row(2, orders=1, homepage='1'), row(3, orders=1)])
        self.assertEqual(r['email_promotion_share'], 1 / 3)
        self.assertEqual(r['homepage_feature_share'], 1 / 3)
        self.assertIsNone(promotion_share([]))
        with self.assertRaises(ValueError):
            promotion_share([0, 2])

    def test_sample_cv_definition(self):
        result = coefficient_of_variation([1, 3])
        self.assertEqual(result['mean_orders'], 2)
        self.assertAlmostEqual(result['sample_std_orders'], math.sqrt(2))
        self.assertAlmostEqual(result['cv'], math.sqrt(2) / 2)
        self.assertEqual(coefficient_of_variation([3, 3])['cv'], 0)

    def test_cv_unavailable_for_empty_single_zero_and_low_mean(self):
        for values in [[], [3], [0, 0], [1e-14, 2e-14]]:
            result = coefficient_of_variation(values)
            self.assertIsNone(result['cv'])
            self.assertIsNotNone(result['unavailable_reason'])

    def test_cv_invalid_values_rejected(self):
        for values in [[-1, 3], [float('nan'), 2], [float('inf'), 1]]:
            with self.assertRaises(ValueError):
                coefficient_of_variation(values)

    def test_grouping_pools_observed_center_meal_weeks(self):
        r = calculate_kpis([row(1, meal='1', orders=1), row(2, week=3, meal='1', orders=3), row(3, meal='2', orders=2)])
        first, second = r['volatility']
        self.assertEqual(first['observations'], 2)
        self.assertEqual(first['observed_centers'], 2)
        self.assertEqual(first['observed_weeks'], 2)
        self.assertAlmostEqual(first['cv'], math.sqrt(2) / 2)
        self.assertIsNone(second['cv'])

    def test_invalid_price_coverage_does_not_silently_report_full_revenue(self):
        r = calculate_kpis([row(1, checkout='bad', orders=3), row(2, checkout='10', base='0', orders=2), row(3, checkout='10', base='20', orders=1)])
        self.assertEqual(r['total_orders'], 6)
        self.assertIsNone(r['revenue_proxy'])
        self.assertEqual(r['valid_row_revenue_proxy_subtotal'], '30')
        self.assertEqual(r['revenue_invalid_rows'], 1)
        self.assertEqual(r['revenue_excluded_orders'], 3)
        self.assertEqual(r['discount_invalid_rows'], 2)
        self.assertEqual(r['discount_excluded_orders'], 5)
        self.assertEqual(r['discount_mean_rate'], .5)

    def test_discount_mean_is_unweighted_and_includes_negative_rows(self):
        r = calculate_kpis([row(1, checkout='80', base='100', orders=1000), row(2, checkout='110', base='100', orders=1)])
        self.assertAlmostEqual(r['discount_mean_rate'], .05)
        self.assertEqual(r['negative_discount_rows'], 1)
        self.assertEqual(r['values_clamped'], 0)

    def test_empty_input_undefined_ratios(self):
        r = calculate_kpis([])
        self.assertEqual(r['total_orders'], 0)
        for field in ['average_weekly_demand','revenue_proxy','discount_mean_rate','email_promotion_share','homepage_feature_share']:
            self.assertIsNone(r[field])

    def test_duplicate_and_nonbinary_input_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            calculate_kpis([row(1), row(1)])
        with self.assertRaisesRegex(ValueError, 'binary'):
            calculate_kpis([row(1, email='2')])


if __name__ == '__main__':
    unittest.main()
