import unittest
import numpy as np

from src.statistics.promotions import (block_intervals, contrast, mw_reference,
                                        percentage_difference, spearman_reference)


def record(week,orders,email=0,discount=0):
    return dict(week=week,orders=orders,email=email,discount=discount)


class PromotionTests(unittest.TestCase):
    def test_context_weighting_not_pooled_volume_weighting(self):
        groups={'a':[record(1,100,0),record(2,200,1)],
                'b':[record(1,10,0),record(2,10,0),record(3,20,1)]}
        r=contrast(groups,lambda r:r['email'],1,0,min_per_state=1,bootstrap=False)
        self.assertEqual(r['reference_context_mean'],55)
        self.assertEqual(r['promoted_context_mean'],110)
        self.assertEqual(r['percentage_difference'],100)
        self.assertEqual(r['coverage']['comparison_rows'],5)

    def test_missing_state_and_insufficient_samples_accounted(self):
        groups={'a':[record(1,2),record(2,3)],'b':[record(1,4),record(2,8,1)]}
        r=contrast(groups,lambda r:r['email'],1,0,min_per_state=2,bootstrap=False)
        self.assertFalse(r['available'])
        self.assertEqual(r['coverage']['contexts_lacking_a_state'],1)
        self.assertEqual(r['coverage']['contexts_with_both_but_below_minimum'],1)

    def test_mann_whitney_ties_and_orientation(self):
        r=mw_reference([2,3],[1,2])
        self.assertEqual(r['u'],3.5)
        self.assertEqual(r['probability_superiority_pooled'],.875)
        self.assertIn('IID reference only',r['calibration'])

    def test_rank_tests_insufficient_or_constant(self):
        self.assertIsNone(mw_reference([1],[2])['u'])
        self.assertIsNone(spearman_reference([1,1,1],[1,2,3])['rho'])
        self.assertIsNone(spearman_reference([1,2],[2,3])['rho'])

    def test_spearman_rank_direction(self):
        self.assertAlmostEqual(spearman_reference([1,2,3],[3,2,1])['rho'],-1)

    def test_invalid_rank_inputs(self):
        with self.assertRaises(ValueError): spearman_reference([1,2,3],[1,2])
        with self.assertRaises(ValueError): mw_reference([1,float('nan')],[1,2])

    def test_percentage_zero_baseline(self):
        self.assertIsNone(percentage_difference(10,0))
        self.assertEqual(percentage_difference(8,10),-20)

    def test_negative_discount_preserved_in_summaries(self):
        groups={'a':[record(1,10,0,-.2),record(2,20,1,.1),record(3,10,0,-.1),record(4,20,1,.2)]}
        r=contrast(groups,lambda r:r['email'],1,0,min_per_state=2,bootstrap=False)
        self.assertAlmostEqual(r['discount_reference']['mean'],-.15)
        self.assertEqual(r['coverage']['input_orders'],60)

    def test_bootstrap_deterministic_and_constant_effect(self):
        r=block_intervals(10,20,np.zeros(12),repetitions=100,lengths=(4,8))
        self.assertEqual(r,block_intervals(10,20,np.zeros(12),repetitions=100,lengths=(4,8)))
        self.assertEqual(r['sensitivity'][0]['difference_ci95'],[10,10])
        self.assertEqual(r['sensitivity'][0]['percentage_ci95'],[50,50])

    def test_nonconsecutive_global_weeks_rejected_for_block_inference(self):
        groups={'a':[record(1,10),record(3,20,1)]}
        with self.assertRaisesRegex(ValueError,'consecutive'):
            contrast(groups,lambda r:r['email'],1,0,min_per_state=1)


if __name__=='__main__': unittest.main()
