"""Phase 12 export of verified results; no analytical/model refitting."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from src.analysis.plots import weekly_figure,pareto_figure,center_figure
from src.analysis.kpis import discount_rate

ROOT=Path(__file__).resolve().parents[1]
BLUE='#246b85'; GREY='#aab7bd'; ORANGE='#b9691c'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(relative): return json.loads((ROOT/relative).read_text(encoding='utf-8'))
def footer(fig,text):
    fig.supxlabel(text,fontsize=10)
def save(fig,name):
    path=ROOT/'reports/figures'/name
    fig.savefig(path,dpi=180,facecolor='white')
    axes=[]
    for ax in fig.axes:
        axes.append({'titles':[ax.get_title(loc=loc) for loc in ['left','center','right']],
                     'xlabel':ax.get_xlabel(),'ylabel':ax.get_ylabel(),'texts':[t.get_text() for t in ax.texts],
                     'ylim':list(map(float,ax.get_ylim())),'xlim':list(map(float,ax.get_xlim())),
                     'xscale':ax.get_xscale(),'yscale':ax.get_yscale(),
                     'lines':[{'x':np.asarray(line.get_xdata(),dtype=float).tolist(),'y':np.asarray(line.get_ydata(),dtype=float).tolist()} for line in ax.lines],
                     'bars':[{'width':float(bar.get_width()),'height':float(bar.get_height())} for bar in ax.patches if hasattr(bar,'get_height')]})
    evidence={'figure_texts':[t.get_text() for t in fig.texts],'axes':axes}
    plt.close(fig)
    return {'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'render_evidence':evidence}

def main():
    snapshot=ROOT/'data/processed/phase12/before.json'
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        raw={p.name:sha(p) for p in (ROOT/'data/raw').glob('*.csv')}
        assert raw==load('docs/phase5_audit.json')['raw_sha256_before']
        protected=list((ROOT/'tests').glob('*.py'))+list((ROOT/'src').rglob('*.py'))+list((ROOT/'notebooks').glob('*.ipynb'))+[ROOT/'requirements.txt']
        snapshot.write_text(json.dumps({'raw_before':raw,'protected_before':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in protected},'volume_figure_before':sha(ROOT/'reports/figures/demand_volume_volatility.png')},indent=2)+'\n')
    before=load('data/processed/phase12/before.json')
    assert {p.name:sha(p) for p in (ROOT/'data/raw').glob('*.csv')}==before['raw_before']
    a=load('data/processed/phase6/eda_results.json'); p=load('data/processed/phase8/promotion_results.json'); v=load('data/processed/phase9/inventory_segments.json')
    for phase in [6,7,8,9,10]: assert load(f'docs/phase{phase}_validation.json')['status']=='passed'
    prepared=ROOT/'data/processed/train_prepared.csv'; assert sha(prepared)==a['prepared_sha256']==v['prepared_sha256']
    plt.rcParams.update({'font.size':11,'axes.titlesize':16,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,'axes.spines.top':False})
    figures={}
    # Reuse the existing two-panel weekly figure and its verified data.
    fig=weekly_figure(a); ax=fig.axes[0]; peak=a['weekly_summary']['peak']; trough=a['weekly_summary']['trough']
    ax.set_ylim(0,peak['orders']/1e6*1.28)
    ax.annotate(f"Peak: {peak['orders']:,} orders",(peak['week'],peak['orders']/1e6),xytext=(15,22),textcoords='offset points',arrowprops={'arrowstyle':'-','color':BLUE},fontsize=11)
    ax.annotate(f"Week {trough['week']}: {trough['orders']:,}",(trough['week'],trough['orders']/1e6),xytext=(12,-24),textcoords='offset points',arrowprops={'arrowstyle':'-','color':BLUE},fontsize=10)
    fig.axes[1].set_xlabel('Week index (calendar dates unavailable)')
    footer(fig,'Source: validated historical demand, weeks 1–145. Only recorded orders are shown.\nAssortment and observation coverage vary; absent meal-center weeks are not filled with zero.')
    figures['weekly']=save(fig,'weekly_demand.png')
    # Improve the existing category Pareto rather than introduce another view.
    fig=pareto_figure(a,'categories','Categories');ax,right=fig.axes; c=a['categories'];n=c['threshold_count']
    plt.setp(ax.get_xticklabels(),fontsize=10,rotation=45,ha='right')
    ax.set_ylim(0,max(x['orders'] for x in c['ranking'])/1e6*1.16)
    right.set_ylim(0,105);right.lines[0].set_label('Cumulative demand');right.lines[1].set_label('80% reference')
    right.legend(loc='center right',fontsize=10,framealpha=.95)
    ax.text(.30,.66,f"{', '.join(c['selected_keys'][:3])},\n{', '.join(c['selected_keys'][3:])}: {c['selected_share_pct']:.2f}% combined",transform=ax.transAxes,va='top',fontsize=11,bbox={'facecolor':'white','edgecolor':'#d0d9dd','alpha':.97,'pad':8})
    footer(fig,'Source: validated historical demand, weeks 1–145. Bars: total orders; orange line: cumulative share.\nBlue bars include the category that takes the combined share past 80%; all categories are shown.')
    figures['category']=save(fig,'category_pareto.png')
    # Reuse the existing center view as a sixth complementary final chart.
    fig=center_figure(a);ax=fig.axes[0];leader=a['centers'][0]
    ax.set_title('')
    ax.set_title(f"Center {leader['center_id']} leads recorded demand",loc='left',pad=15)
    ax.set_xlim(0,leader['average_observed_week_orders']*1.25)
    ax.text(.98,.13,f"Center {leader['center_id']}: {leader['average_observed_week_orders']:,.0f} orders\nper observed week",transform=ax.transAxes,ha='right',va='center',fontsize=11,bbox={'facecolor':'white','edgecolor':'#d0d9dd','pad':8})
    footer(fig,'Source: validated historical demand, weeks 1–145. Top 10 centers by total orders; bars show weekly averages.\nCenter IDs are coded labels. Assortment, operating area and coverage differ; this is not an efficiency ranking.')
    figures['centers']=save(fig,'center_demand.png')
    # Existing Phase 8 results contain no promotion figure: plot the validated matched-context means.
    fig,axes=plt.subplots(1,2,figsize=(12.5,7),sharey=True,layout='constrained')
    fig.suptitle('Promotion weeks show higher demand within the same meal and center',fontsize=17)
    for ax,flag,label in zip(axes,['email','homepage'],['Email promotion','Homepage featuring']):
        r=p[flag]; means=[r['reference_context_mean'],r['promoted_context_mean']]
        bars=ax.bar([0,1],means,color=[GREY,BLUE],width=.58)
        ax.set(title=label,xticks=[0,1],xticklabels=['Email absent','Email present'] if flag=='email' else ['Not featured','Featured'],ylim=(0,840))
        for bar,value,pooled in zip(bars,means,[r['pooled_reference'],r['pooled_promoted']]):
            ax.text(bar.get_x()+bar.get_width()/2,value+12,f"{value:.1f}\nn={pooled['n']:,} records",ha='center',va='bottom',fontsize=10)
        ax.text(.04,.95,f"{r['percentage_difference']:+.1f}% observed difference\n{r['coverage']['eligible_series']:,} comparable meal-center groups",transform=ax.transAxes,va='top',fontsize=11,fontweight='bold')
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Average orders per recorded meal-center-week\n(meal-center groups weighted equally)')
    footer(fig,'Source: validated historical comparisons, weeks 1–145; at least 5 records per promotion state in each group.\nEmail and homepage comparisons use different groups. Discounts, timing and other promotions also differ.\nThese are observed associations; the differences cannot be attributed to promotion alone.')
    figures['promotion']=save(fig,'promotion_comparison.png')
    # Render every recorded observation; signed discounts and full demand range are preserved.
    frame=pd.read_csv(prepared,usecols=['base_price','checkout_price','num_orders'])
    assert (frame.base_price>0).all() and np.isfinite(frame.to_numpy()).all()
    discount=pd.Series([float(discount_rate(str(base),str(checkout)))*100 for base,checkout in zip(frame.base_price,frame.checkout_price)],index=frame.index)
    assert len(frame)==p['rows']==456548 and int((discount<0).sum())==p['negative_discounts']==116101
    fig,ax=plt.subplots(figsize=(12,7.5),layout='constrained')
    density=ax.hexbin(discount,frame.num_orders,gridsize=(65,45),yscale='log',bins='log',mincnt=1,cmap='viridis')
    assert int(density.get_array().sum())==len(frame),'All observations must contribute to density'
    ax.axvline(0,color='#555555',ls='--',lw=1)
    ax.set(title='Discounts have only a weak positive association with demand',xlabel='Discount rate (%)\nNegative values mean checkout price exceeds base price',ylabel='Observed orders per meal-center-week (log scale)',xlim=(-80,105),ylim=(10,30000))
    ax.set_yticks([10,100,1000,10000]);ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.text(.02,.97,f"Spearman rank correlation: {p['spearman']['rho']:.3f}\nAll {len(frame):,} recorded meal-center-weeks",transform=ax.transAxes,va='top',fontsize=11,bbox={'facecolor':'white','edgecolor':'#d0d9dd','alpha':.96,'pad':8})
    cb=fig.colorbar(density,ax=ax,pad=.025);cb.set_label('Recorded observations per hexagon\n(logarithmic color scale)');cb.set_ticks([1,10,100,1000,10000]);cb.ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    footer(fig,f"Source: validated historical observations, weeks 1–145. All {p['negative_discounts']:,} negative discounts are retained.\nDemand and density colors use log scales to show sparse and dense regions; no observations are omitted.\nThis pooled relationship also reflects meal/center mix and promotion overlap; it does not establish causation.")
    figures['discount']=save(fig,'discount_demand.png')
    retained=ROOT/'reports/figures/demand_volume_volatility.png'
    assert sha(retained)==before['volume_figure_before']
    figures['inventory']={'file':str(retained.relative_to(ROOT)).replace('\\','/'),'sha256':sha(retained),'unchanged':True}
    for file,value in before['protected_before'].items(): assert sha(ROOT/file)==value,file
    assert {f.name:sha(f) for f in (ROOT/'data/raw').glob('*.csv')}==before['raw_before']
    result={'status':'exported; pending independent numerical and visual validation','figures':figures,'source_result_hashes':{x:sha(ROOT/x) for x in ['data/processed/phase6/eda_results.json','data/processed/phase8/promotion_results.json','data/processed/phase9/inventory_segments.json']},'density_observations':int(density.get_array().sum()),'full_suite_rerun':False}
    (ROOT/'data/processed/phase12/export_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'figures':{k:v['file'] for k,v in figures.items()},'density_observations':result['density_observations']},indent=2))

if __name__=='__main__':main()
