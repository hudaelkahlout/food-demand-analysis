import unittest
import numpy as np
import pandas as pd
from src.machine_learning.forecast import (features,history_of,temporal_split,recursive_forecast,
    nonnegative,make_model,check_frame,FEATURES)
from sklearn.metrics import mean_absolute_error

def fixture():
    return pd.DataFrame([dict(id=w,week=w,center_id=1,meal_id=2,checkout_price=12.,base_price=10.,
        emailer_for_promotion=0,homepage_featured=1,category='Rice',cuisine='Indian',center_type='A',
        city_code=1,region_code=2,op_area=3.,num_orders=float(w*10)) for w in range(1,16)])

class ForecastTests(unittest.TestCase):
    def test_split(self):
        a,b=temporal_split(fixture()); self.assertEqual((a.week.max(),b.week.min(),len(b)),(5,6,10))
    def test_exact_week_and_missing_not_zero(self):
        d=fixture(); h=history_of(d.loc[d.week!=4]); x=features(d.loc[d.week==5],h)
        self.assertTrue(x.lag_1.isna().all()); self.assertEqual(x.prior_4_count.iloc[0],3)
        self.assertEqual(x.prior_4_mean.iloc[0],20)
    def test_current_future_target_invariance(self):
        d=fixture(); rows=d.loc[d.week==5]; a=features(rows,history_of(d))
        d.loc[d.week>=5,'num_orders']=1e9
        pd.testing.assert_frame_equal(a,features(rows,history_of(d)))
    def test_recursive_ignores_holdout_targets(self):
        d=fixture(); fit,hold=temporal_split(d); a,_=recursive_forecast(None,fit,hold,30)
        hold['num_orders']=999999; b,_=recursive_forecast(None,fit,hold,30)
        np.testing.assert_array_equal(a,b); np.testing.assert_array_equal(a,np.full(10,50.))
    def test_fallback_without_zero(self):
        d=fixture(); fit=d.loc[d.week<=5]; future=d.loc[d.week==7]
        a,info=recursive_forecast(None,fit,future,30); self.assertEqual(a[0],30); self.assertEqual(info['missing_previous_week'],1)
    def test_order_and_overlap(self):
        d=fixture(); fit,hold=temporal_split(d); hold=hold.iloc[::-1]
        a,_=recursive_forecast(None,fit,hold,30); self.assertEqual(len(a),len(hold))
        with self.assertRaises(ValueError): recursive_forecast(None,d,hold,30)
    def test_finite_nonnegative(self):
        np.testing.assert_array_equal(nonnegative([-3,4]),[0,4])
        with self.assertRaises(ValueError): nonnegative([np.inf])
    def test_validation(self):
        d=fixture(); check_frame(d,True)
        with self.assertRaises(ValueError): check_frame(pd.concat([d,d]),True)
        d.loc[0,'emailer_for_promotion']=2
        with self.assertRaises(ValueError): check_frame(d,True)
    def test_no_target_or_id_feature(self):
        self.assertNotIn('id',FEATURES); self.assertNotIn('num_orders',FEATURES)
        d=fixture(); x=features(d,history_of(d)); self.assertTrue((x.discount_rate<0).all())
    def test_pipeline_training_only_and_unknown_category(self):
        d=fixture(); fit=d.iloc[:5]; x=features(fit,history_of(fit)); model=make_model('Linear Regression').fit(x,fit.num_orders)
        self.assertEqual(model.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute'].statistics_[0],3)
        future=d.iloc[5:6].copy(); future['category']='unseen'; out=model.predict(features(future,history_of(fit)))
        self.assertTrue(np.isfinite(out).all())
    def test_mae(self):
        self.assertEqual(mean_absolute_error([1,4,7],[2,2,10]),2)
    def test_multiseries_alignment_and_recursive_updates(self):
        d=fixture(); second=d.copy(); second['id']+=100; second['meal_id']=3; second['num_orders']*=2
        all_rows=pd.concat([d,second],ignore_index=True)
        fit=all_rows.loc[all_rows.week<=5]; future=all_rows.loc[all_rows.week>5].iloc[::-1]
        a,_=recursive_forecast(None,fit,future,30)
        np.testing.assert_array_equal(a,np.where(future.meal_id==2,50.,100.))
    def test_rolling_excludes_current_and_cross_series(self):
        d=fixture(); h=history_of(d); h[(5,1,3)]=1e10
        x=features(d.loc[d.week==5],h)
        self.assertEqual(x.prior_4_mean.iloc[0],25.)
        self.assertEqual(x.lag_1.iloc[0],40.)
    def test_invalid_denominator_is_missing(self):
        d=fixture(); d.loc[0,'base_price']=0; d.loc[1,'base_price']=-1
        x=features(d,history_of(d)); self.assertTrue(x.discount_rate.iloc[:2].isna().all())
    def test_forest_determinism(self):
        d=fixture(); x=features(d,history_of(d)); a=make_model('Random Forest'); b=make_model('Random Forest')
        a.fit(x,d.num_orders); b.fit(x,d.num_orders)
        np.testing.assert_array_equal(a.predict(x),b.predict(x))

if __name__=='__main__': unittest.main()
