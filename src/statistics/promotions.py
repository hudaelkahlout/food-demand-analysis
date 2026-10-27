"""Phase 8. Fixed-context descriptive effects and week-block uncertainty."""

from collections import defaultdict
import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats

from src.analysis.demand import file_hash
from src.analysis.kpis import discount_rate

FLAGS = ('emailer_for_promotion', 'homepage_featured')
STATES = ('neither', 'email_only', 'homepage_only', 'both')


def percentage_difference(promoted, reference):
    return 100 * (promoted - reference) / reference if reference else None


def summary(values):
    x = np.asarray(values, dtype=float)
    return {'n': len(x), 'mean': float(x.mean()) if len(x) else None,
            'median': float(np.median(x)) if len(x) else None,
            'q25': float(np.quantile(x,.25)) if len(x) else None,
            'q75': float(np.quantile(x,.75)) if len(x) else None}


def mw_reference(x, y):
    """IID reference only; repeated rows do not support its calibration."""
    if not all(np.isfinite(v) for v in list(x)+list(y)):
        raise ValueError('Rank-test samples must be finite')
    if min(len(x),len(y)) < 2:
        return {'u': None, 'iid_reference_p': None, 'reason': 'fewer than two observations in a state'}
    result=stats.mannwhitneyu(x,y,alternative='two-sided',method='asymptotic',use_continuity=True)
    return {'u': float(result.statistic), 'iid_reference_p': float(result.pvalue),
            'p_underflow': bool(result.pvalue==0),
            'probability_superiority_pooled': float(result.statistic/(len(x)*len(y))),
            'calibration': 'IID reference only: serial dependence, shared weeks, and context mixture invalidate a confirmatory interpretation'}


def spearman_reference(x,y):
    if len(x)!=len(y) or not all(np.isfinite(v) for v in list(x)+list(y)):
        raise ValueError('Spearman requires aligned finite pairs')
    if len(x)<3 or len(set(x))<2 or len(set(y))<2:
        return {'n': len(x), 'rho': None, 'iid_reference_p': None, 'reason': 'insufficient nonconstant paired values'}
    r=stats.spearmanr(x,y)
    return {'n':len(x),'rho':float(r.statistic),'iid_reference_p':float(r.pvalue),
            'p_underflow':bool(r.pvalue==0),'calibration':'IID reference only; repeated observations mean confirmatory significance is not established'}


def block_intervals(effect, baseline, weekly_scores, *, repetitions=2000, seed=20261027, lengths=(4,8,12)):
    """Linearized fixed-context contrast; resample common week-score blocks.

    Weekly scores are mean residual contrasts using fixed original per-state
    sample counts. This is a first-order bootstrap of the same ratio estimator,
    not a bootstrap that silently changes eligible contexts when a state vanishes.
    """
    scores=np.asarray(weekly_scores,dtype=float)
    if len(scores)<2 or repetitions<100:
        return {'available':False,'reason':'insufficient weeks or repetitions'}
    records=[]
    for length in lengths:
        length=min(length,len(scores)); rng=np.random.default_rng(seed)
        starts=rng.integers(0,len(scores),size=(repetitions,int(np.ceil(len(scores)/length))))
        indices=((starts[:,:,None]+np.arange(length))%len(scores)).reshape(repetitions,-1)[:,:len(scores)]
        draws=effect+scores[indices].sum(axis=1)
        low,high=np.quantile(draws,[.025,.975]); flo,fhi=np.quantile(draws,[.005,.995])
        records.append({'block_weeks':length,'repetitions':repetitions,'seed':seed,
                        'difference_ci95':[float(low),float(high)],'difference_ci99_family5':[float(flo),float(fhi)],
                        'percentage_ci95':[float(100*low/baseline),float(100*high/baseline)] if baseline else None,
                        'family99_excludes_zero': bool(flo>0 or fhi<0)})
    return {'available':True,'method':'Linearized circular moving-week-block bootstrap; same week draws for all contexts, fixed eligible contexts; 95% pointwise and 99% intervals for five predeclared contrasts',
            'score_sum':float(scores.sum()),'assumptions':'Approximate weakly dependent/stationary week-score process; drift, longer dependence and observational confounding remain; circular wrapping is computational, not calendar seasonality',
            'weekly_score_lag1_correlation':float(np.corrcoef(scores[:-1],scores[1:])[0,1]) if np.std(scores[:-1])>0 and np.std(scores[1:])>0 else None,
            'primary_block_weeks':8,'sensitivity':records}


def contrast(groups, selector, promoted, reference, *, min_per_state=5, eligible_keys=None, bootstrap=True):
    """Equal-context means; pooled row summaries remain separately labeled."""
    if min_per_state<1:
        raise ValueError('Minimum observations per state must be positive')
    eligible=[]
    state_counts=[(sum(selector(r)==promoted for r in rows),sum(selector(r)==reference for r in rows)) for rows in groups.values()]
    for key, rows in sorted(groups.items()):
        if eligible_keys is not None and key not in eligible_keys:
            continue
        x=[r for r in rows if selector(r)==promoted]; y=[r for r in rows if selector(r)==reference]
        if len(x)>=min_per_state and len(y)>=min_per_state:
            eligible.append((key,x,y))
    all_rows=[r for rows in groups.values() for r in rows]
    used=[r for _,x,y in eligible for r in x+y]
    accounting={'input_series':len(groups),'eligible_series':len(eligible),'excluded_series':len(groups)-len(eligible),
                'input_rows':len(all_rows),'comparison_rows':len(used),'rows_outside_comparison':len(all_rows)-len(used),
                'input_orders':sum(r['orders'] for r in all_rows),'comparison_orders':sum(r['orders'] for r in used),
                'orders_outside_comparison':sum(r['orders'] for r in all_rows)-sum(r['orders'] for r in used),
                'min_observations_per_state_per_context':min_per_state,
                'contexts_lacking_a_state':sum(min(x,y)==0 for x,y in state_counts),
                'contexts_with_both_but_below_minimum':sum(0<min(x,y)<min_per_state for x,y in state_counts),
                'no_rows_deleted_from_source':True}
    if not eligible:
        return {'available':False,'reason':'no contexts with sufficient observations in both states','coverage':accounting}
    means1=np.array([np.mean([r['orders'] for r in x]) for _,x,y in eligible])
    means0=np.array([np.mean([r['orders'] for r in y]) for _,x,y in eligible])
    mean1,mean0=float(means1.mean()),float(means0.mean()); difference=mean1-mean0
    px=[r for _,x,y in eligible for r in x]; py=[r for _,x,y in eligible for r in y]
    weeks=sorted({r['week'] for r in all_rows}); index={w:i for i,w in enumerate(weeks)}
    # Scores retain actual global week positions; missing observations add no residual.
    if weeks != list(range(min(weeks),max(weeks)+1)):
        raise ValueError('Block inference requires consecutive global weeks; do not bridge gaps')
    scores=np.zeros(len(weeks)); auc=[]
    for i,(_,x,y) in enumerate(eligible):
        for rows,mean,sign in [(x,means1[i],1),(y,means0[i],-1)]:
            for r in rows:
                scores[index[r['week']]]+=sign*(r['orders']-mean)/len(rows)/len(eligible)
        # U/(n1*n0) is descriptive even for one-observation states; no p-value
        # is needed for this context-weighted probability-of-superiority summary.
        u=stats.mannwhitneyu([r['orders'] for r in x],[r['orders'] for r in y],method='asymptotic').statistic
        auc.append(float(u/(len(x)*len(y))))
    return {'available':True,'coverage':accounting,'weighting':'Each eligible center-meal context receives equal weight in both means; observed weeks unweighted within each state',
            'promoted_context_mean':mean1,'reference_context_mean':mean0,'difference_orders':difference,
            'percentage_difference':percentage_difference(mean1,mean0),
            'median_context_difference':float(np.median(means1-means0)),
            'mean_within_context_probability_superiority':float(np.mean(auc)),
            'pooled_promoted':summary([r['orders'] for r in px]),'pooled_reference':summary([r['orders'] for r in py]),
            'mann_whitney_pooled_reference':mw_reference([r['orders'] for r in px],[r['orders'] for r in py]),
            'discount_promoted':summary([r['discount'] for r in px]),'discount_reference':summary([r['discount'] for r in py]),
            'uncertainty':block_intervals(difference,mean0,scores) if bootstrap else {'available':False,'reason':'not requested'}}


def load_records(root):
    root=Path(root); source=root/'data/processed/train_prepared.csv'
    expected=json.loads((root/'docs/phase5_audit.json').read_text())['outputs']['train_prepared.csv']['sha256']
    if file_hash(source)!=expected: raise ValueError('Prepared source hash mismatch')
    records=[]; seen=set()
    with source.open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream):
            key=(row['center_id'],row['meal_id']); logical=(key,int(row['week']))
            if logical in seen: raise ValueError('Duplicate context-week')
            seen.add(logical)
            discount=discount_rate(row['base_price'],row['checkout_price'])
            if discount is None: raise ValueError('Invalid discount denominator requires an explicit missing-data design')
            e,h=int(row[FLAGS[0]]),int(row[FLAGS[1]])
            if e not in (0,1) or h not in (0,1): raise ValueError('Nonbinary flag')
            records.append({'key':key,'week':int(row['week']),'orders':int(row['num_orders']),
                            'discount':float(discount),'email':e,'homepage':h,'state':STATES[e+2*h] if e+h<2 else 'both'})
    if file_hash(source)!=expected: raise ValueError('Prepared source changed')
    return records


def analyze(root):
    root=Path(root); records=load_records(root); groups=defaultdict(list)
    for row in records: groups[row['key']].append(row)
    result={'phase':8,'rows':len(records),'total_orders':sum(r['orders'] for r in records),
            'negative_discounts':sum(r['discount']<0 for r in records),'contexts':len(groups),
            'design':{'minimum_per_state':5,'predeclared_contrasts':5,'alpha':.05,'family_intervals':.99,
                      'bootstrap_repetitions':2000,'bootstrap_seed':20261027,'block_lengths':[4,8,12],
                      'interpretation':'Conditional observed association, not adjusted for discounts or time; IID p-values are references only'}}
    for flag in ('email','homepage'):
        result[flag]=contrast(groups,lambda r:r[flag],1,0)
        result[flag]['global_context_only']={str(value):summary([r['orders'] for r in records if r[flag]==value]) for value in (0,1)}
        result[flag]['overlap']={str(value):{'rows':sum(r[flag]==value for r in records),
                                          'discount':summary([r['discount'] for r in records if r[flag]==value]),
                                          'other_flag_share':float(np.mean([r['homepage' if flag=='email' else 'email'] for r in records if r[flag]==value]))}
                                 for value in (0,1)}
    common={key for key,rows in groups.items() if all(sum(r['state']==state for r in rows)>=5 for state in STATES)}
    global_states={state:{'demand':summary([r['orders'] for r in records if r['state']==state]),
                          'discount':summary([r['discount'] for r in records if r['state']==state]),
                          'contexts':len({r['key'] for r in records if r['state']==state})} for state in STATES}
    result['combined']={'global_states':global_states,'common_four_state_contexts':len(common),
                        'sufficient_for_comparison':len(common)>=30,
                        'comparison_rule':'At least 5 observations per state in a common context; at least 30 common contexts for descriptive contrasts (not proof of inferential independence)',
                        'contrasts':{}}
    if len(common)>=30:
        for state in STATES[1:]:
            result['combined']['contrasts'][state]=contrast(groups,lambda r:r['state'],state,'neither',eligible_keys=common)
    result['spearman']=spearman_reference([r['discount'] for r in records],[r['orders'] for r in records])
    within=[]; within_rows=within_orders=0
    for rows in groups.values():
        rho=spearman_reference([r['discount'] for r in rows],[r['orders'] for r in rows])
        if len(rows)>=10 and rho['rho'] is not None:
            within.append(rho['rho']); within_rows+=len(rows); within_orders+=sum(r['orders'] for r in rows)
    result['spearman']['within_context']={'eligible_contexts':len(within),'excluded_contexts':len(groups)-len(within),
                                         'eligible_rows':within_rows,'excluded_rows':len(records)-within_rows,
                                         'eligible_orders':within_orders,'excluded_orders':result['total_orders']-within_orders,
                                         'mean_rho_equal_context':float(np.mean(within)),'median_rho':float(np.median(within)),
                                         'positive_contexts':sum(x>0 for x in within),
                                         'interpretation':'Descriptive distribution of within-context monotonic associations, not a pooled adjusted correlation or combined significance test'}
    output=root/'data/processed/phase8';output.mkdir(exist_ok=True)
    (output/'promotion_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
