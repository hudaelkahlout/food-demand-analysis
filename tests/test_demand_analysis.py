"""Deterministic tests of Phase 6 denominators, coverage and concentration."""

import unittest
from src.analysis.demand import analyze_records, concentration, weekly_changes


def row(identity, week, center, meal, orders, kind='A', area='2', category='Food'):
    return dict(id=str(identity), week=str(week), center_id=center, meal_id=meal,
                num_orders=str(orders), center_type=kind, op_area=area, category=category)


class AnalysisTests(unittest.TestCase):
    def test_changes_do_not_fill_or_bridge_missing_week(self):
        values = weekly_changes({1: 100, 3: 200, 4: 300})
        self.assertEqual([r['week'] for r in values], [1, 3, 4])
        self.assertIsNone(values[1]['change_pct'])
        self.assertEqual(values[2]['change_orders'], 100)
        self.assertEqual(values[2]['change_pct'], 50)

    def test_zero_denominator_is_unavailable(self):
        self.assertIsNone(weekly_changes({1: 0, 2: 10})[1]['change_pct'])

    def test_threshold_includes_crossing_group(self):
        result = concentration({'a': 60, 'b': 25, 'c': 15})
        self.assertEqual(result['selected_keys'], ['a', 'b'])
        self.assertEqual(result['selected_share_pct'], 85)
        self.assertEqual(result['previous_share_pct'], 60)

    def test_exact_threshold_and_deterministic_ties(self):
        result = concentration({'b': 10, 'c': 10, 'a': 80})
        self.assertEqual(result['threshold_count'], 1)
        self.assertEqual([r['key'] for r in result['ranking']], ['a', 'b', 'c'])

    def test_undefined_or_invalid_concentration_rejected(self):
        for totals, target in [({}, .8), ({'a': 0}, .8), ({'a': -1, 'b': 10}, .8), ({'a': 1}, 0)]:
            with self.assertRaises(ValueError):
                concentration(totals, target)

    def test_center_week_is_sum_of_meals_and_no_zero_fill(self):
        result = analyze_records([row(1, 1, 'c', 'a', 10), row(2, 1, 'c', 'b', 20),
                                  row(3, 3, 'c', 'a', 50), row(4, 2, 'd', 'a', 100, 'B', '4')])
        center = next(r for r in result['centers'] if r['center_id'] == 'c')
        self.assertEqual(center['observed_weeks'], 2)
        self.assertEqual(center['average_observed_week_orders'], 40)
        self.assertEqual(center['missing_global_weeks'], 1)
        self.assertEqual(result['missing_weeks_filled'], 0)
        self.assertTrue(all(v == 180 for v in result['partition_order_totals'].values()))

    def test_type_denominator_is_observed_center_weeks(self):
        result = analyze_records([row(1, 1, 'c', 'a', 10), row(2, 2, 'c', 'a', 30), row(3, 1, 'd', 'a', 80)])
        kind = result['center_types'][0]
        self.assertEqual(kind['centers'], 2)
        self.assertEqual(kind['observed_center_weeks'], 3)
        self.assertEqual(kind['orders_per_observed_center_week'], 40)
        self.assertEqual(kind['median_center_weekly_average'], 50)

    def test_duplicate_observation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            analyze_records([row(1, 1, 'c', 'a', 10), row(2, 1, 'c', 'a', 20)])

    def test_conflicting_lookup_attribute_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Conflicting center'):
            analyze_records([row(1, 1, 'c', 'a', 10), row(2, 2, 'c', 'a', 20, area='3')])

    def test_no_record_and_negative_demand_rejected(self):
        for rows in [[], [row(1, 1, 'c', 'a', -1)]]:
            with self.assertRaises(ValueError):
                analyze_records(rows)


if __name__ == '__main__':
    unittest.main()
