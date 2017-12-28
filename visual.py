import pandas as pd
from bokeh.io import show,output_notebook,output_file, export_png
from bokeh.models import (DatetimeTickFormatter,Range1d,ColumnDataSource, HoverTool, CategoricalColorMapper,
	FixedTicker,FuncTickFormatter,ColorBar,LinearColorMapper)
from bokeh.plotting import figure
from bokeh.palettes import Viridis256
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
import pickle
import datetime as dt
import os



def probtoclass(series,hold):
	return [1 if i>=hold else 0 for i in series]

def no_lamp(data):
	lamp = []
	for i in set(data['kp']):
		if str(i)[-1]!='0':
			lamp.append(i)
	return data[~data['kp'].isin(lamp)]

def ind_to_datetime(d):
	rick = pickle.load(open('../../data_2017/FCNN/rick.pickle','rb'))
	morty = {v:k for k,v in rick['time'].iteritems()}
	d['time_ind']=d['time']
	d['time']=[morty[t].split(':')[0]+morty[t].split(':')[1] for t in d['time']]
	d['dtime'] = pd.to_datetime(d['date']+' '+d['time'])
	return d

def kp_to_ind(d):
	kp_index={i: ind for ind, i in enumerate(sorted(list(set(d['kp']))))}
	d['kp_ind']=d['kp'].replace(kp_index)
	return d

def ensemble_class(prob1, prob2, prob1_weight, threshold):
	return probtoclass((prob1*prob1_weight)+(prob2*(1-prob1_weight)), threshold)

def preprocess_data(d): 
	d.rename(columns={'p_status':'fcnn_prob','p_status_rf':'rf_prob'},inplace=True)
	d['kp']=['{:07.3f}'.format(v) for v in d.kp]
	d['rf_prob'] = d['rf_prob'].apply(lambda x: float(x.split(' ')[-1][:-1]))
	
	if highway=='D1110':
		d['en_prob']=(d['rf_prob']*0.3+d['fcnn_prob']*0.7)
		d['en_status'] = probtoclass(d.en_prob,0.36) #f1:0.5 recall:0.36
		d['rf_status'] = probtoclass(d.rf_prob,0.2)
	else:
		d['en_prob']=(d['rf_prob']*0.4+d['fcnn_prob']*0.6)
		d['en_status'] = probtoclass(d.en_prob,0.4) #f1:0.4 recall:0.2
		d['rf_status'] = probtoclass(d.rf_prob,0.1)

	d['fcnn_status'] = probtoclass(d.fcnn_prob,0.7)

	d['en_status'].replace({0:'free_flow', 1:'congestion'},inplace=True)
	d['rf_status'].replace({0:'free_flow', 1:'congestion'},inplace=True)
	d['fcnn_status'].replace({0:'free_flow', 1:'congestion'},inplace=True)
	d['status'].replace({0:'free_flow', 1:'mix',2:'congestion'},inplace=True)

	return ind_to_datetime(kp_to_ind(d))

def visual_data(od,date,lamp_in=True): #lamp_in: include lamp kp in data
	d = od.loc[od['date']==date,:]
	if lamp_in==True:
		pass
	else:
		d = no_lamp(d)
	d['kp']=['{:6.2f}'.format(float(v)) for v in d.kp]
	return d





def make_figure(d): #arg{'fcnn','rf','en'}


	mapper2 = CategoricalColorMapper(palette=['white','#933b41'],
                               factors=['free_flow','congestion'])
	for k in ['fcnn','rf','en']:
		source = ColumnDataSource(d)

		p= figure(title='{}_0{}_{}'.format(highway,direction,date),
			x_range= list(sorted(set(d['kp']))),
			y_range=Range1d(start = list(reversed(list(sorted(set(d['dtime'])))))[0],end =list(reversed(list(sorted(set(d['dtime'])))))[-1]),
			y_axis_type='datetime', plot_height = 288*3,
			x_axis_location='above',
			plot_width = 20*len((set(d['kp']))))

		p.rect('kp','dtime',
			width=1,height=1000*60*5,source=source,
			fill_color={'field':'{}_status'.format(k),'transform':mapper2},fill_alpha = 0.5,
			line_color=None,legend='{}_status'.format(k))
		p.xaxis.axis_label= 'KP(km)'
		#p.xaxis.formatter= PrintfFormatter(format='{}')
		p.yaxis.axis_label= 'Time'
		p.yaxis.formatter = DatetimeTickFormatter(hours =['%H:%M'],days=['%H:%M'],months=['%H:%M'],years=['%H:%M'])
		p.ygrid[0].ticker.desired_num_ticks =24
		p.toolbar.logo = None
		p.xaxis.major_label_orientation = 45
		p.toolbar.logo=None
		p.toolbar_location=None
		
		try:
			os.mkdir('../../summary/result_/_pngfile/{}'.format(k))
		except OSError:
			pass
		try:	
			os.mkdir('../../summary/result_/_pngfile/{}/{}_0{}'.format(k,highway,direction))
		except OSError:
			pass


		export_png(p,filename='../../summary/result_/_pngfile/{}/{}_0{}/{}_0{}_{}.png'.format(k,highway,direction,highway,direction,date))
		

highways =['D1110']
for highway in highways:
	year=17
	if highway == 'D1110':
		directions = [4,5]
	else:
		directions = [3]

	for direction in directions:
		# od=pd.read_csv('../../summary/result_/original_csv/{}_{}_newyear.csv'.format(highway,direction),header=0,dtype={'kp':str},engine='python')
		# od['dtime']=pd.to_datetime(od['dtime'])

		od = pd.read_csv('../../testing_2017/traffic_peak_season/noyear_{}_{}_{}.csv'.format(highway,year,direction), header=0,usecols=[0,1,2,3,7,15,16])
		od = preprocess_data(od)

		od.to_csv('../../summary/result_/_original_csv/{}_{}_newyear.csv'.format(highway,direction),header=True, index=None)

		dates = list(sorted(list(set(od['date']))))
		for date in dates:
			print highway,direction,date
			d = visual_data(od, date, lamp_in=False)
			make_figure(d)

#correlation heatmap
def corr_heatmap(df,output_html):
    df_corr = df.corr().unstack().dropna().reset_index()
    df_corr.columns=['x','y','corr']
    
    toolbar = 'hover,save,pan,box_zoom,reset,wheel_zoom'
    source =  ColumnDataSource(df_corr)
    mapper = LinearColorMapper(palette=Viridis256,high=1,low=-1)
    p = figure(tools=toolbar,toolbar_sticky=False,
               x_range=df_corr.x.unique(),y_range=df_corr.y.unique(),
              width=900,height=800)
    p.rect(x='x',y='y',width=1,height=1,source=source, fill_color={'field':'corr','transform':mapper},
           fill_alpha=0.7,line_color=None)
    
    colorb = ColorBar(color_mapper=mapper,location=(0,0),scale_alpha=0.7)
    p.add_layout(colorb,'right')
    p.xaxis.major_label_orientation = 45
    
    p.grid.grid_line_alpha=0
    
    hover = p.select_one(HoverTool)
    hover.tooltips = [('feature_0','@x'),("feature_1","@y"),("corr","@corr")]
    
    output_file(output_html)
    save(p)

#autocorrelation (make sure no multiple kp data mix together)
def auto_corr(dd,target_col,outputname,showfig=True, savefig=True):
    t_col = target_col
    
    fig, ax = plt.subplots(nrows=4,figsize=(15,30))
    fig.suptitle('{}'.format(outputname))
    plot_acf(dd[t_col],lags=72,unbiased=True,alpha=0.05,ax=ax[0])
    ax[0].set_title('6 hr')
    ax[0].set_ylabel('correlation')
    ax[0].set_xlabel('lag(5min)')
    plot_acf(dd[t_col],lags=288*1,unbiased=True,alpha=0.05,ax=ax[1])
    ax[1].set_title('1 day')
    ax[1].set_ylabel('correlation')
    ax[1].set_xlabel('lag(5min)')
    plot_acf(dd[t_col],lags=288*3,unbiased=True,alpha=0.05,ax=ax[2])
    ax[2].set_title('3 day')
    ax[2].set_ylabel('correlation')
    ax[2].set_xlabel('lag(5min)')
    plot_acf(dd[t_col],lags=288*7,unbiased=True,alpha=0.05,ax=ax[3])
    ax[3].set_title('1 week')
    ax[3].set_ylabel('correlation')
    ax[3].set_xlabel('lag(5min)')
    if savefig:
    	plt.savefig('{}.png'.format(outputname))
    if showfig:
		plt.show()








