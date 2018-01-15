# coding: utf-8
from __future__ import division
import pandas as pd
import datetime as dt
import pickle
from bokeh.io import show,output_notebook,output_file,save
from bokeh.models import (DatetimeTickFormatter,Range1d,ColumnDataSource, HoverTool, CategoricalColorMapper,
                          LinearAxis,FixedTicker,FuncTickFormatter,PrintfTickFormatter,ColorBar)
from bokeh.plotting import figure
import os


def status_rect(data,direction,kp_fc,name='traffic map',origin_column='origin_ststus',
                predict_column='predict_status',datetime_column='datetime',time_unit=5):
    #the input dataframe must contain a 'datetime' type column for y axis
    #if no prediction, predict=False
    #check the categories of colormapper and hover tooltips
    
    lane= origin_column.split('_')[0]
    
    data['date'] = data[datetime_column].dt.date.astype(str)
    
    kplist = list(sorted(set(data['kp'])))
    ws={}
    fkp={}
    kpac=0
    for ind, kp in enumerate(kplist):
        if ind ==0:
            ws[kp]=kp+((kplist[ind+1]-kp)/2)
        elif kp == kplist[-1]:
            ws[kp]=((kp-kplist[ind-1])/2)*2
        else:
            ws[kp]=((kp-kplist[ind-1])/2)+((kplist[ind+1]-kp)/2)
        fkp[kp]=kpac+(ws[kp]/2)
        kpac+=ws[kp]
            
    data['width']=data.kp.replace(ws)
    data['f_kp']=data.kp.replace(fkp)
    
    source = ColumnDataSource(data)
    
    toolbar = 'hover,save,pan,box_zoom,reset,wheel_zoom'
    
    
    #the base-plot setting
    p= figure(title=name,
              x_range= Range1d(end = max(kplist)+ws[max(kplist)],start =0),
              y_range=Range1d(start = max(data[datetime_column]),end =min(data[datetime_column])),
              y_axis_type='datetime', plot_height = (len(data[datetime_column].unique())*3)+100,
              x_axis_location='above',tools=toolbar,
              plot_width = 20*len(kplist))
    
    p.xaxis.axis_label= 'KP(km)'
    p.yaxis.axis_label= 'Time'
    p.yaxis.formatter = DatetimeTickFormatter(minutes=['%Y-%m-%d %H:%M'], days=['%Y-%m-%d %H:%M'],hours =['%Y-%m-%d %H:%M'],
                                              months=['%Y-%m-%d %H:%M'],years=['%Y-%m-%d %H:%M'])
    p.ygrid[0].ticker.desired_num_ticks = int(len(data[datetime_column].unique())/12)
    p.toolbar.logo = None
    p.xaxis.major_label_orientation = 45
    p.xaxis.ticker = kplist
    
    #set axis for facility
    p.extra_x_ranges={'facility':Range1d(end = max(kplist)+ws[max(kplist)],start =0)}
    p.add_layout(LinearAxis(x_range_name='facility',axis_label='facility',
                            ticker=list(kp_fc.keys()),major_label_orientation = 45,
                            formatter=FuncTickFormatter(code="""var kpfc_dict = %s;return kpfc_dict[tick];""" %kp_fc)),
                 'below')
                 
    hover = p.select_one(HoverTool)

    #draw rectangles for original status
    mapper = CategoricalColorMapper(palette=['#cc7878','#c9d9d3','#550b1d','#933b41'],
                                    factors=['congestion','free_flow','traffic_jam','conditional'])
    p.rect('f_kp',datetime_column,
           width='width',height=1000*60*time_unit,source=source,
           fill_color={'field':origin_column,'transform':mapper},fill_alpha = 0.3,
           line_color=None,legend=origin_column)
    
    if predict_column!=None:
    #draw rectangles for predict status
        mapper2 = CategoricalColorMapper(palette=['#c9d9d3','yellow'],
                                         factors=['p_free_flow','p_traffic_jam'])
        p.rect('f_kp','dtime',
               width='width',height=1000*60*time_unit,source=source,
               fill_color={'field':predict_column,'transform':mapper2},fill_alpha = 0.2,
               line_color=None,legend=predict_column)
        
        hover.tooltips = [('kp','@kp'),("date","@date"),("time","@time"),('lane',lane),('speed',"@{}_speed".format(lane)),
                          ('car_vol','@{}_carvol'.format(lane)),('occ','@{}_occ'.format(lane)),
                          ('status','@{}'.format(origin_column)),('p_status','@{}'.format(predict_column))]
    else:
        hover.tooltips = [('kp','@kp'),("date","@date"),("time","@time"),('lane',lane),('speed',"@{}_speed".format(lane)),
                          ('car_vol','@{}_carvol'.format(lane)),('occ','@{}_occ'.format(lane)),
                          ('status','@{}'.format(origin_column))]
      
    output_file('/data/projects/Highway/NEXCO_2017/2_visualization/traffic_per_kp_map/{}.html'.format(name))
    #show(p)
    save(p)


def kp_fc_dict(fcdata, highway,direction):
	fc=fcdata.loc[(fcdata['highway_code']==highway)&(fcdata['direction']==direction),['facility_romaji','kp_from','kp_to']]
	fcdict=fc.set_index('facility_romaji').to_dict()['kp_from']
	fcdict0=fc[fc.kp_to!=0].set_index('facility_romaji').to_dict()['kp_to']
	rvfcdict = {v:k for k,v in fcdict.items()}
	rvfcdict0 = {v:k for k,v in fcdict0.items()}
	rvfcdict.update(rvfcdict0)

	return rvfcdict


project_path = '/data/projects/Highway/NEXCO_2017/'

highway = 'D1800'
direction = 3
year= 2016
months = [8]
days = [11]
target_col = 'drive1_status' #need to be a status column

fc = pd.read_csv(os.path.join(project_path,'1_data/data_profiling/kp_coordinates/fc_romaji_processed.csv'))
kpfc_dict = kp_fc_dict(fc,highway,direction)

print 'load data: {} {} {}'.format(highway, year, direction)
d = pd.read_csv(os.path.join(project_path,
	'1_data/engineered_data/road_status_filled_labeled/{}/{}_{}_direction{}.csv'.format(highway,highway,year,direction)), header=0)

d['datetime'] = pd.to_datetime(d['datetime'])
dd = d[(d.datetime.dt.month.isin(months)) & (d.datetime.dt.day.isin(days))]

status_rect(dd,direction,name='{}_{}_{}_{}_TEST'.format(highway, direction, year,target_col),origin_column=target_col,
            predict_column=None, datetime_column='datetime', kp_fc=kpfc_dict)



