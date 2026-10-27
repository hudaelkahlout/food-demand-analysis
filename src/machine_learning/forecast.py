"""Chronological fixed-origin forecasting; no holdout targets enter recursion."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

CAT = ['center_id', 'meal_id', 'category', 'cuisine', 'center_type', 'city_code', 'region_code']
NUM = ['week', 'op_area', 'checkout_price', 'base_price', 'discount_rate', 'emailer_for_promotion',
       'homepage_featured', 'lag_1', 'prior_4_mean', 'prior_4_count']
FEATURES = CAT + NUM
RF_CONFIG = dict(n_estimators=40, max_depth=14, min_samples_leaf=5, max_features=0.5, max_samples=0.35, random_state=42, n_jobs=1)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check_frame(frame, target=False):
    required = {'id', 'week', 'center_id', 'meal_id', 'checkout_price', 'base_price',
                'emailer_for_promotion', 'homepage_featured'} | ({'num_orders'} if target else set())
    if not required <= set(frame):
        raise ValueError('Missing required columns')
    if frame[list(required)].isna().any().any() or frame.id.duplicated().any() or frame.duplicated(['week','center_id','meal_id']).any():
        raise ValueError('Missing fields or duplicate keys')
    nums = list(required - {'id'})
    if not np.isfinite(frame[nums].to_numpy(dtype=float)).all():
        raise ValueError('Nonfinite input')
    if target and (frame.num_orders < 0).any():
        raise ValueError('Negative observed orders')
    for col in ['emailer_for_promotion','homepage_featured']:
        if not frame[col].isin([0,1]).all():
            raise ValueError('Invalid promotion flag')

def temporal_split(frame):
    weeks = sorted(frame.week.unique())
    if len(weeks) <= 10 or weeks != list(range(int(min(weeks)), int(max(weeks))+1)):
        raise ValueError('Need contiguous training weeks and >10 weeks')
    cut = weeks[-10]
    return frame.loc[frame.week < cut].copy(), frame.loc[frame.week >= cut].copy()

def features(rows, history):
    """Exact calendar-week lookup; missing records stay NaN, never zero filled.

    History is (week, center, meal)->observed or recursively predicted orders.
    Only strictly prior weeks are read, even if caller provides future records.
    """
    x = rows[CAT + [c for c in NUM[:7] if c != 'discount_rate']].copy()
    base = rows.base_price.to_numpy(float)
    x['discount_rate'] = np.divide(base-rows.checkout_price.to_numpy(float), base,
                                   out=np.full(len(rows), np.nan), where=base>0)
    lag, mean, count = [], [], []
    for w,c,m in rows[['week','center_id','meal_id']].itertuples(index=False, name=None):
        values = [history.get((w-k,c,m), np.nan) for k in range(1,5)]
        observed = [v for v in values if np.isfinite(v)]
        lag.append(values[0]); mean.append(float(np.mean(observed)) if observed else np.nan); count.append(len(observed))
    x['lag_1'], x['prior_4_mean'], x['prior_4_count'] = lag, mean, count
    return x[FEATURES]

def history_of(rows):
    return {(w,c,m): float(y) for w,c,m,y in rows[['week','center_id','meal_id','num_orders']].itertuples(index=False,name=None)}

def make_model(name):
    numeric = Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True)), ('scale',StandardScaler())])
    pre = ColumnTransformer([('numeric',numeric,NUM), ('categories',OneHotEncoder(handle_unknown='ignore'),CAT)], sparse_threshold=1.0)
    reg = LinearRegression() if name == 'Linear Regression' else RandomForestRegressor(**RF_CONFIG)
    return Pipeline([('preprocess',pre),('regressor',reg)])

def nonnegative(values):
    values = np.asarray(values,dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite predictions')
    return np.maximum(values,0)

def recursive_forecast(model, history_rows, future_rows, fallback):
    """Ten-week fixed origin; discard any future target column on entry."""
    if int(history_rows.week.max()) >= int(future_rows.week.min()):
        raise ValueError('History overlaps prediction window')
    future = future_rows.drop(columns=['num_orders'],errors='ignore').copy()
    history = history_of(history_rows)
    output = pd.Series(index=future.index,dtype=float)
    absent = clipped = 0
    for week in sorted(future.week.unique()):
        batch = future.loc[future.week == week]
        x = features(batch,history)
        absent += int(x.lag_1.isna().sum())
        pred = x.lag_1.fillna(fallback).to_numpy() if model is None else model.predict(x)
        clipped += int((pred < 0).sum())
        pred = nonnegative(pred)
        output.loc[batch.index] = pred
        for (c,m),y in zip(batch[['center_id','meal_id']].itertuples(index=False,name=None),pred):
            history[(week,c,m)] = float(y)
    return output.to_numpy(), {'missing_previous_week':absent, 'negative_predictions_clipped':clipped}

def load_data(root):
    root = Path(root)
    expected = json.loads((root/'docs/phase5_audit.json').read_text())['raw_sha256_before']
    for name,value in expected.items():
        if digest(root/'data/raw'/name) != value:
            raise ValueError('Raw source hash mismatch')
    prepared = root/'data/processed/train_prepared.csv'
    if digest(prepared) != '52467bcad7b7c863276d1844bfe8a677cbfd4d6d08256d704e8da1e4a79cf137':
        raise ValueError('Prepared source mismatch')
    train = pd.read_csv(prepared); test = pd.read_csv(root/'data/raw/test.csv')
    check_frame(train,True); check_frame(test)
    if set(train.id) & set(test.id):
        raise ValueError('Train/test ID overlap')
    audits = []
    for filename,key in [('meal_info.csv','meal_id'),('fulfilment_center_info.csv','center_id')]:
        lookup = pd.read_csv(root/'data/raw'/filename)
        before = len(test); before_ids = test.id.tolist(); unique_before = int(test.id.nunique()); unmatched = int((~test[key].isin(lookup[key])).sum())
        test = test.merge(lookup,on=key,how='left',sort=False,validate='many_to_one')
        audits.append(dict(lookup=filename,before=before,after=len(test),unmatched=unmatched,duplicate_expansion=len(test)-before,orders_total_before='not applicable',orders_total_after='not applicable',unique_ids_before=unique_before,unique_ids_after=int(test.id.nunique()),lookup_unique_keys=int(lookup[key].nunique()),lookup_rows=len(lookup),row_order_preserved=test.id.tolist()==before_ids))
        if unmatched or len(test)!=before or test.id.tolist()!=before_ids:
            raise ValueError('Test join failure')
    return train,test,audits,expected

def run(root):
    root = Path(root); out = root/'data/processed/phase10'; out.mkdir(parents=True,exist_ok=True)
    train,test,joins,hashes = load_data(root)
    fit,hold = temporal_split(train)
    x = features(fit,history_of(fit)); fallback = float(fit.num_orders.median())
    metrics = {}; predictions = hold[['id','week','center_id','meal_id','num_orders']].copy(); fitted = {}
    for name in ['Previous-week baseline','Linear Regression','Random Forest']:
        print('Evaluating '+name,flush=True)
        model = None
        if name != 'Previous-week baseline':
            model = make_model(name); model.fit(x,fit.num_orders); fitted[name] = model
        pred,info = recursive_forecast(model,fit,hold,fallback)
        predictions[name] = pred
        metrics[name] = dict(mae=float(mean_absolute_error(hold.num_orders,pred)),**info)
    baseline = metrics['Previous-week baseline']['mae']
    for result in metrics.values():
        result['improvement_pct_vs_baseline'] = 100*(baseline-result['mae'])/baseline
    winner = min(metrics,key=lambda name:metrics[name]['mae'])
    # Descriptive model interpretation, never used for choosing/tuning the model.
    interpretation = {}
    for name,model in fitted.items():
        names = model.named_steps['preprocess'].get_feature_names_out()
        reg = model.named_steps['regressor']
        values = reg.coef_ if name=='Linear Regression' else reg.feature_importances_
        order = np.argsort(np.abs(values))[::-1][:20]
        interpretation[name] = [{'feature':str(names[i]),'value':float(values[i])} for i in order]
    print('Refitting selected model: '+winner,flush=True)
    final = None
    if winner != 'Previous-week baseline':
        final = make_model(winner); final.fit(features(train,history_of(train)),train.num_orders)
    test_pred,info = recursive_forecast(final,train,test,float(train.num_orders.median()))
    pd.DataFrame({'id':test.id.to_numpy(),'num_orders':test_pred}).to_csv(out/'test_predictions.csv',index=False)
    predictions.to_csv(out/'holdout_predictions.csv',index=False)
    weekly = []
    for week,part in predictions.groupby('week',sort=True):
        weekly.append({'week':int(week),'rows':len(part),**{name:float(np.mean(np.abs(part.num_orders-part[name]))) for name in metrics}})
    result = dict(design='fixed-origin recursive ten-week forecast; no holdout actual updates',
        fit_weeks=[int(fit.week.min()),int(fit.week.max())],holdout_weeks=[int(hold.week.min()),int(hold.week.max())],
        fit_rows=len(fit),holdout_rows=len(hold),fit_orders=int(fit.num_orders.sum()),holdout_orders=int(hold.num_orders.sum()),
        source_rows=len(train),source_orders=int(train.num_orders.sum()),excluded_rows=0,
        features=FEATURES,feature_validation=dict(fit_missing_counts={c:int(v) for c,v in x.isna().sum().items()},train_checkout_above_base=int((train.checkout_price>train.base_price).sum()),test_checkout_above_base=int((test.checkout_price>test.base_price).sum()),training_feature_max_week=int(fit.week.max()),holdout_targets_used_for_features=False,test_targets_available=False),random_forest_configuration=RF_CONFIG,metrics=metrics,winner=winner,
        fallback_fit_median=fallback,test_summary=dict(rows=len(test),weeks=[int(test.week.min()),int(test.week.max())],
            minimum=float(test_pred.min()),maximum=float(test_pred.max()),mean=float(test_pred.mean()),total=float(test_pred.sum()),**info),
        joins=joins,weekly_mae=weekly,interpretation=interpretation,raw_hashes=hashes,
        versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__))
    for name,value in hashes.items():
        assert digest(root/'data/raw'/name)==value
    assert np.isfinite(test_pred).all() and (test_pred>=0).all()
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    run(Path(__file__).resolve().parents[2])


