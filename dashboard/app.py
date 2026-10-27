"""Streamlit client dashboard; run from repository root as documented."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
import streamlit as st
from dashboard.data import load_bundle,filter_history,summarize_selection,forecast_selection,SECTIONS
st.set_page_config(page_title='Food Demand | Planning',page_icon='🍽️',layout='wide')

@st.cache_data(show_spinner='Loading verified planning data…')
def bundle():return load_bundle()
@st.cache_data(show_spinner='Updating selected demand…',max_entries=12)
def summary(frame,full):return summarize_selection(frame,full)

def image(name):st.image(str(ROOT/'reports/figures'/name),width='stretch')
def metrics(items):
    for col,(label,value,help_text) in zip(st.columns(len(items)),items):
        with col:st.metric(label,value,help=help_text,border=True)
def reset_history():
    for key in ['hist_weeks','hist_categories','hist_meals','hist_centers','hist_types','hist_cuisines','hist_promotion']:
        st.session_state.pop(key,None)
def selected_history(frame):
    st.sidebar.divider();st.sidebar.caption('These filters apply only to Demand and Centers.')
    weeks=st.sidebar.slider('Historical weeks',1,145,(1,145),key='hist_weeks')
    categories=st.sidebar.multiselect('Category',sorted(frame.category.unique()),key='hist_categories')
    meals=st.sidebar.multiselect('Meal ID',sorted(frame.meal_id.unique()),key='hist_meals',help='Meal names are not supplied; IDs identify meals.')
    centers=st.sidebar.multiselect('Center ID',sorted(frame.center_id.unique()),key='hist_centers')
    types=st.sidebar.multiselect('Center type',sorted(frame.center_type.unique()),key='hist_types')
    cuisines=st.sidebar.multiselect('Cuisine',sorted(frame.cuisine.unique()),key='hist_cuisines')
    promotion=st.sidebar.selectbox('Promotion status',['All','Email present','Homepage featured','Neither','Both'],key='hist_promotion')
    st.sidebar.button('Reset historical filters',on_click=reset_history,width='stretch')
    st.sidebar.caption('An empty category/ID/type selection includes all values.')
    selected,audit=filter_history(frame,weeks,categories,meals,centers,types,cuisines,promotion)
    st.caption(f"Selected: {len(selected):,} observed records · {audit['selected_orders']:,} orders · weeks {weeks[0]}–{weeks[1]}. Missing observations stay absent.")
    with st.expander('Selection coverage'):
        st.write(f"{audit['source_rows']:,} source records → {audit['selected_rows']:,} selected; {audit['outside_selection_rows']:,} outside this view. Source data is unchanged.")
        st.write(f"Orders: {audit['source_orders']:,} source = {audit['selected_orders']:,} selected + {audit['outside_selection_orders']:,} outside.")
    if selected.empty:st.info('No recorded observations match these filters. Broaden the selection or reset filters.');st.stop()
    return selected,summary(selected,b['demand'])

st.sidebar.title('Food demand')
section=st.sidebar.radio('Explore',SECTIONS,key='section')
st.sidebar.caption('Historical observations: weeks 1–145. Forecasts: weeks 146–155. Week numbers are not calendar dates.')
try:b=bundle()
except (FileNotFoundError,ValueError,KeyError) as error:
    st.error('The verified planning data is unavailable. See dashboard/README.md for the required local files.');st.caption(str(error));st.stop()
st.title(section)

if section=='Overview':
    k=b['kpis'];st.caption('Full historical portfolio · 145 observed weeks · 456,548 recorded meal-center-weeks')
    metrics([('Total orders',f"{k['total_orders']:,}",'All recorded historical orders.'),('Average weekly demand',f"{k['average_weekly_demand']:,.0f}",'Total orders divided by 145 observed weeks; absent records are not filled.'),('Revenue proxy',f"{float(k['revenue_proxy'])/1e9:.2f} billion",'Checkout price × orders; currency unspecified. This is not profit.')])
    metrics([('Mean signed discount',f"{k['discount_mean_rate']:.2%}",'Unweighted mean of signed (base − checkout) / base; negative discounts are retained.'),('Email promotion share',f"{k['email_promotion_share']:.2%}",'Share of observed records with email flag present, not share of orders.'),('Homepage feature share',f"{k['homepage_feature_share']:.2%}",'Share of observed records with homepage flag present, not share of orders.')])
    st.info('Revenue is a price-times-orders proxy. Currency is unspecified; costs, margins and profit are unavailable.')
    st.subheader('Demand is concentrated, while weekly requirements vary')
    st.write('Five categories account for 81.40% of recorded demand. Use Demand to explore the mix by center and meal, and Forecasting to review expected weekly orders.')
    image('weekly_demand.png')
    st.caption('Historical evidence supports planning review; it does not measure achieved waste or stockout reductions.')

elif section=='Demand':
    selected,a=selected_history(b['history'])
    peak=a['weekly_summary']['peak'];st.subheader(f"Selected demand peaks in week {peak['week']} at {peak['orders']:,} orders")
    weekly=pd.DataFrame(a['weekly'])
    st.line_chart(weekly,x='week',y='orders',x_label='Week index',y_label='Observed orders',color='#246b85',width='stretch')
    st.caption('Observed weekly totals only; lines connect recorded weeks. Missing records remain absent, and week indices do not establish calendar seasonality.')
    c=a['categories'];st.subheader(f"{c['threshold_count']} categories account for {c['selected_share_pct']:.2f}% of selected demand")
    cats=pd.DataFrame(c['ranking']).rename(columns={'key':'Category','orders':'Orders','cumulative_pct':'Cumulative share (%)'})
    st.bar_chart(cats,x='Category',y='Orders',horizontal=True,sort=False,x_label='Observed orders',y_label='Category',color='#246b85')
    st.caption('Categories are ranked by orders. The 80% group includes the category crossing the threshold.')
    st.dataframe(cats[['Category','Orders','Cumulative share (%)']],hide_index=True,width='stretch',column_config={'Orders':st.column_config.NumberColumn(format='localized'),'Cumulative share (%)':st.column_config.NumberColumn(format='%.2f')})
    m=a['meals'];st.subheader(f"{m['threshold_count']} meals account for {m['selected_share_pct']:.2f}% of selected demand")
    top=st.slider('Meals shown',5,51,15,key='top_meals')
    meals=pd.DataFrame(m['ranking']);meals['Meal ID']=meals['key'].astype(str)
    st.bar_chart(meals.head(top),x='Meal ID',y='orders',horizontal=True,sort=False,x_label='Observed orders',y_label='Coded meal ID',color='#246b85')
    st.caption(f"Showing {min(top,len(meals))} of {len(meals)} selected meals; the concentration calculation uses all selected meals.")
    st.dataframe(meals[['Meal ID','category','orders','cumulative_pct']].rename(columns={'category':'Category','orders':'Orders','cumulative_pct':'Cumulative share (%)'}),hide_index=True,width='stretch')

elif section=='Centers':
    st.info('Center 13 is the full-history volume leader: 4,296,545 orders, or 29,631 orders per observed week. Rankings below follow the selected view.')
    selected,a=selected_history(b['history']);rows=pd.DataFrame(a['centers']);leader=rows.iloc[0]
    st.subheader(f"Center {leader.center_id} leads the selected view by total orders")
    mode=st.radio('Compare centers by',['Total orders','Orders per observed week'],horizontal=True,key='center_measure')
    value='orders' if mode=='Total orders' else 'average_observed_week_orders'
    view=rows.sort_values(value,ascending=False).head(15).copy();view['Center ID']=view.center_id.astype(str);view=view.rename(columns={value:mode})
    st.bar_chart(view,x='Center ID',y=mode,horizontal=True,sort=False,x_label=mode,y_label='Coded center ID',color='#246b85')
    st.caption('Top 15 in the chosen measure. Demand reflects assortment, coverage and operating area; this is not an efficiency ranking.')
    st.dataframe(rows[['center_id','center_type','orders','observed_weeks','average_observed_week_orders']].rename(columns={'center_id':'Center ID','center_type':'Center type','orders':'Total orders','observed_weeks':'Observed weeks','average_observed_week_orders':'Orders per observed week'}),hide_index=True,width='stretch')
    types=pd.DataFrame(a['center_types']);lead=types.loc[types.orders_per_observed_center_week.idxmax()]
    st.subheader(f"{lead.center_type} leads selected orders per observed center-week")
    type_view=types.rename(columns={'center_type':'Center type','orders':'Total orders','orders_per_observed_center_week':'Orders per observed center-week','centers':'Centers','observed_center_weeks':'Observed center-weeks'})
    left,right=st.columns(2)
    with left:
        st.bar_chart(type_view,x='Center type',y='Total orders',x_label='Center type',y_label='Total observed orders',color='#246b85')
    with right:
        st.bar_chart(type_view,x='Center type',y='Orders per observed center-week',x_label='Center type',y_label='Orders per observed center-week',color='#246b85')
    st.caption('Totals reflect unequal center counts. Weekly averages use observed center-weeks, not absent weeks filled with zero. Type differences are descriptive.')
    st.dataframe(type_view[['Center type','Centers','Observed center-weeks','Orders per observed center-week']],hide_index=True,width='stretch')

elif section=='Promotions & Pricing':
    st.caption('Fixed historical comparison populations · weeks 1–145 · Demand/Center filters do not apply here')
    st.warning('These are observed associations, not causal effects. Discounts, timing, availability and other promotions also differ.')
    image('promotion_comparison.png')
    st.write('Each comparable meal-center group receives equal weight. Email and homepage panels use different eligible groups; their percentages do not rank channel effectiveness.')
    for flag,label in [('email','Email'),('homepage','Homepage')]:
        r=b['promotions'][flag]
        with st.expander(f'{label}: comparison coverage'):
            st.write(f"{r['coverage']['eligible_series']:,} comparable meal-center groups; at least five records per state. {r['pooled_promoted']['n']:,} flagged and {r['pooled_reference']['n']:,} reference records.")
    states=b['promotions']['combined']['global_states']
    combined=pd.DataFrame([{'Condition':key.replace('_',' ').title(),'Average orders':row['demand']['mean'],'Records':row['demand']['n']} for key,row in states.items()])
    st.subheader('Weeks with both promotion flags have the highest pooled average demand')
    st.bar_chart(combined,x='Condition',y='Average orders',x_label='Promotion condition',y_label='Orders per recorded meal-center-week',color='#246b85')
    st.caption('Unadjusted pooled averages across all recorded rows, not the equal-group comparisons above. Different meals, centers and discounts contribute to each condition; this is not evidence of synergy.')
    st.dataframe(combined,hide_index=True,width='stretch')
    image('discount_demand.png')
    st.caption('Negative discounts are preserved. A weak pooled relationship cannot establish how an individual price change would affect demand.')

elif section=='Inventory Risk':
    inv=b['inventory'];st.caption('Fixed historical portfolio screening · weeks 1–145 · Demand/Center filters do not change these thresholds')
    st.info('14 priority meals combine high observed volume and high relative variation, representing 45.93% of historical orders.')
    image('demand_volume_volatility.png')
    st.write('High volume means at least 1,489,681 recorded orders; high volatility means CV at least 0.87774049. CV is the sample standard deviation divided by the mean and includes variation between centers as well as weeks.')
    indexed={r['meal_id']:r for r in inv['meals']};priority=pd.DataFrame([indexed[i] for i in inv['priority_meal_ids']])
    st.subheader('All 14 priority meals, ordered by demand volume')
    st.dataframe(priority[['meal_id','category','cuisine','orders','cv','segment']].rename(columns={'meal_id':'Meal ID','category':'Category','cuisine':'Cuisine','orders':'Observed orders','cv':'CV','segment':'Segment'}),hide_index=True,width='stretch',column_config={'Observed orders':st.column_config.NumberColumn(format='localized'),'CV':st.column_config.NumberColumn(format='%.3f')})
    st.caption('Meal names were not supplied. Review both volume and variation; lead times, inventory and shelf-life data are unavailable, so exact safety-stock quantities cannot be inferred.')
    with st.expander('All meal segments'):
        st.dataframe(pd.DataFrame(inv['meals'])[['meal_id','category','orders','cv','segment']].rename(columns={'meal_id':'Meal ID','category':'Category','orders':'Observed orders','cv':'CV','segment':'Segment'}),hide_index=True,width='stretch')

elif section=='Forecasting':
    ml=b['ml'];win=ml['winner'];improvement=ml['metrics'][win]['improvement_pct_vs_baseline']
    st.success(f"{win} is the best holdout model: {improvement:.2f}% lower MAE than the previous-week baseline.")
    st.caption('Fit weeks 1–135; fixed-origin recursive evaluation on weeks 136–145. All three models use the same 32,821 observed holdout rows.')
    metrics([('Random Forest MAE',f"{ml['metrics']['Random Forest']['mae']:.2f} orders",'Average absolute error per observed meal-center-week on the ten-week holdout.'),('Improvement vs baseline',f'{improvement:.2f}%','Lower mean absolute error on the chronological holdout, not a guaranteed future improvement.')])
    comp=pd.DataFrame([{'Model':name,'MAE (orders)':row['mae'],'Improvement vs baseline (%)':row['improvement_pct_vs_baseline']} for name,row in ml['metrics'].items()])
    st.subheader('Random Forest has the lowest observed holdout error')
    st.bar_chart(comp,x='Model',y='MAE (orders)',x_label='Forecast method',y_label='Mean absolute error (orders)',color='#246b85')
    st.dataframe(comp,hide_index=True,width='stretch',column_config={'MAE (orders)':st.column_config.NumberColumn(format='%.2f'),'Improvement vs baseline (%)':st.column_config.NumberColumn(format='%.2f')})
    st.caption('Lower is better. Each prediction used only information available at the forecast origin and earlier recursive predictions; the winning model was then refitted through week 145.')
    held=b['holdout'].groupby('week',sort=True)[['num_orders','Random Forest']].sum().reset_index().rename(columns={'num_orders':'Actual orders','Random Forest':'Forecast orders'})
    st.subheader('Holdout weekly totals show where forecasts differ from actual orders')
    st.line_chart(held,x='week',y=['Actual orders','Forecast orders'],x_label='Holdout week',y_label='Total orders',color=['#246b85','#b9691c'])
    st.caption('Both lines cover identical observed rows. Aggregate agreement can hide errors for individual meals and centers.')
    st.divider();st.subheader('Future weekly demand to support purchasing review')
    future=b['future'];left,middle,right=st.columns(3)
    with left:center=st.selectbox('Forecast center',['All']+sorted(future.center_id.unique()),key='forecast_center')
    with middle:meal=st.selectbox('Forecast meal',['All']+sorted(future.meal_id.unique()),key='forecast_meal')
    with right:weeks=st.slider('Forecast weeks',146,155,(146,155),key='forecast_weeks')
    selected,audit=forecast_selection(future,center,meal,weeks)
    st.caption(f"{len(selected):,} selected forecast rows; {len(future)-len(selected):,} outside this view. Forecasts are conditional on the supplied pricing/promotion plans.")
    if selected.empty:st.info('No forecast rows match this selection. Choose another meal, center or week range.')
    else:
        metrics([('Selected forecast orders',f'{selected.forecast_orders.sum():,.0f}','Sum of predicted orders over the selected recorded test inputs; not observed demand.')])
        weekly=selected.groupby('week',sort=True).forecast_orders.sum().reset_index().rename(columns={'forecast_orders':'Forecast orders'})
        st.line_chart(weekly,x='week',y='Forecast orders',x_label='Future week',y_label='Forecast orders',color='#246b85')
        display=selected[['week','center_id','meal_id','category','forecast_orders']].rename(columns={'week':'Week','center_id':'Center ID','meal_id':'Meal ID','category':'Category','forecast_orders':'Forecast orders'})
        st.dataframe(display.head(100),hide_index=True,width='stretch',column_config={'Forecast orders':st.column_config.NumberColumn(format='%.1f')})
        st.caption('Preview: first 100 selected rows in original input order. The download includes the full selection.')
        st.download_button('Download selected forecasts',selected[['id','week','center_id','meal_id','category','forecast_orders']].to_csv(index=False).encode('utf-8'),file_name='selected_forecasts.csv',mime='text/csv')
    st.warning('Future inputs have no observed demand, so no test accuracy is available. Forecasts support weekly purchasing review; recipes, stock on hand, lead times and shelf life are needed before deciding purchase quantities.')

st.divider();st.caption('Source: validated meal-delivery observations and forecasts. Currency and operating-area units are unspecified. Coded meal and center IDs do not identify real locations.')
