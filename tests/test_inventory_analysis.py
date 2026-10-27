"""Phase 9 median boundaries, joint risk criteria and conservation tests."""

import unittest
from src.analysis.inventory import SEGMENTS, segment_meals


def meal(identity, orders, cv):
    return dict(meal_id=str(identity), orders=orders, cv=cv, observations=2)


class InventoryTests(unittest.TestCase):
    def test_all_four_quadrants_and_conservation(self):
        r=segment_meals([meal(1,100,.2),meal(2,100,.8),meal(3,10,.2),meal(4,10,.8)],50,.5)
        self.assertEqual([s['meals'] for s in r['segment_summary']],[1,1,1,1])
        self.assertEqual(sum(s['orders'] for s in r['segment_summary']),220)
        self.assertEqual(r['priority_meal_ids'],['2'])
        self.assertEqual(sum(s['observations'] for s in r['segment_summary']),8)

    def test_medians_and_inclusive_boundary(self):
        r=segment_meals([meal(1,10,.1),meal(2,20,.2),meal(3,30,.3)])
        self.assertEqual(r['thresholds']['volume_orders'],20)
        self.assertEqual(r['thresholds']['cv'],.2)
        self.assertEqual(r['meals'][1]['segment'],SEGMENTS[0])

    def test_high_cv_alone_does_not_get_priority(self):
        r=segment_meals([meal(1,1,10),meal(2,100,1),meal(3,200,2)],50,1.5)
        self.assertEqual(r['priority_meal_ids'],['3'])
        self.assertEqual(r['meals'][0]['segment'],SEGMENTS[2])

    def test_priority_order_is_volume_then_cv_then_id(self):
        r=segment_meals([meal(3,100,5),meal(2,100,5),meal(1,200,2)],50,1)
        self.assertEqual(r['priority_meal_ids'],['1','2','3'])

    def test_input_unchanged_and_no_week_imputation(self):
        rows=[meal(1,20,.5),meal(2,10,.1)]
        before=[dict(row) for row in rows]
        r=segment_meals(rows)
        self.assertEqual(rows,before)
        self.assertEqual(r['missing_weeks_filled'],0)

    def test_tied_medians_are_not_artificially_split(self):
        r=segment_meals([meal(1,10,.5),meal(2,10,.5)])
        self.assertEqual(r['segment_summary'][0]['meals'],2)
        self.assertEqual(sum(s['meals'] for s in r['segment_summary']),2)

    def test_invalid_or_undefined_metrics_rejected(self):
        for rows in [[],[meal(1,10,None)],[meal(1,-1,.5)],[meal(1,10,float('nan'))],[meal(1,10,-1)],[meal(1,float('inf'),.5)]]:
            with self.assertRaises(ValueError):segment_meals(rows)

    def test_duplicate_keys_and_invalid_cutoffs_rejected(self):
        with self.assertRaises(ValueError):segment_meals([meal(1,10,.1),meal(1,20,.2)])
        with self.assertRaises(ValueError):segment_meals([meal(1,10,.1)],-1,.2)
        with self.assertRaises(ValueError):segment_meals([meal(1,10,.1)],10,float('inf'))


if __name__=='__main__':unittest.main()
