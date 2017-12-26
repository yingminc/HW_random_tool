# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import numpy as np
import os
import time

#clean the non_numeric data for weather
def dealwithshit(d):
    return d.apply(lambda x: x.split(' ')[0] if isinstance(x,str) else x).replace({'--':0}).apply(pd.to_numeric,errors='coerce')

#tool for filling missing data

def group_numbers(numlist):
    grouplist=[]
    group=[]
    for ind, i in enumerate(numlist):
        
        if ind==0:
            group.append(i)
        elif i-numlist[ind-1]==1:
            #print i
            group.append(i)
        elif i-numlist[ind-1]>1:
            #print i
            grouplist.append(group)
            group=[i]
        if ind == len(numlist)-1:
            grouplist.append(group)
    return grouplist

def length_filter(grouplist,threshold):
    indexes=[]
    for g in grouplist:
        #print len(g)
        if len(g)<=threshold:
            indexes.extend(g)
    return indexes

def fill_index(data, nolanelist,fillrange):
    filltarget=[]
    ranges = range(1,fillrange+1)
    if len(nolanelist)<=fillrange:
        return nolanelist
    else:
        for ind, i in enumerate(nolanelist):
            for r in ranges[::-1]: 
                if i in filltarget:
                    #print r
                    
                    pass
                elif ind ==0:
                    if i not in filltarget:
                        if (data.loc[i,'datetime']!=min(data['datetime']))&((nolanelist[ind+r]-i)>r):
                            filltarget.extend(nolanelist[ind:ind+r+1])
                elif (ind>0)and(ind<(len(nolanelist)-(r+1))):
                    if i not in filltarget:
                        if ((i-nolanelist[ind-(fillrange+1-r)])!=(fillrange+1-r))and((nolanelist[ind+r]-i)>r):
                            filltarget.extend(nolanelist[ind:ind+r+1])
                elif (ind>(len(nolanelist)-(r+1))):
                    if i not in filltarget:
                        if ((i-nolanelist[ind-(fillrange+1-r)])!=(fillrange+1-r)):
                                filltarget.extend(nolanelist[ind:ind+r+1])
        return filltarget

def spot_to_span(dtlist,gapseconds=60*5,fillseconds=60*10):
	start=[]
	end=[]
	dtlist.sort()
	for ind, i in enumerate(dtlist):
		if ind==0:
			start.append(i)
		if (ind<(len(dtlist)-1)):
			if((dtlist[ind+1]-i).seconds>gapseconds):
				end.append(i)
				start.append(dtlist[ind+1])
		elif (ind==len(dtlist)-1):
			end.append(i)
		else:
			pass
	spans = zip(start,end)
	longspans=[]
	for span in spans:
		if (span[1]-span[0]).seconds>fillseconds:
			longspans.append(span)
	return longspans

#tool for finding pair pk
def pair_kp(dt)
	kps = list(dt.columns)[2:]
	lone = []
	pair = []
	for ind, kp in enumerate(kps):
	    if ind < len(kps)-1:
	        if (dt[kp].iloc[[0,-1]].isnull()).all():
	            lone.append(kp)
	        elif (dt[kp].iloc[[0,-1]].isnull()).any():
	            if (dt[kps[ind+1]].iloc[[0,-1]].notnull()).any():
	                if (dt[kps[ind+1]].iloc[[0,-1]].isnull()).any():
	                    pair.append((kp, kps[ind+1]))
	return pair

def test_year(dt, pair)
	testyear={}
	for a, b in pair:
	    aset=set(dt[dt[a].notnull()].year)
	    bset=set(dt[dt[b].notnull()].year)
	    if (aset).union(bset)==set(dt.year):
	        if len((aset).intersection(bset))>0:
	            common = list(aset.intersection(bset))
	            testyear[(a,b)]=common
	            aset.remove(common[0])
	            bset.remove(common[0])
	            if '2004' in aset:
	                testyear[(a,b)].extend([max(aset),min(bset)])
	            else:
	                testyear[(a,b)].extend([max(bset),min(aset)])
	            
	        else:
	            if '2004' in aset:
	                testyear[(a,b)]=list([max(aset),min(bset)])
	            else:
	                testyear[(a,b)]=list([max(bset),min(aset)])
	return test_year

#for filting kps
def data_filter(data, direction='both',ramp='exclude', drive1_threshold=1):
	if direction == 'both':
		if ramp == 'exclude':
			return d[(d.line==1)&(d.drive1_percentage<=drive1_threshold)].reset_index()

		elif ramp == 'include':
			return d[(d.drive1_percentage<=drive1_threshold)].reset_index()

		elif ramp == 'only':
			return d[(d.line==0)&(d.drive1_percentage<=drive1_threshold)].reset_index()

		else:
			raise AttributeError('ramp options: exclude, include or only')

	else:
		if ramp == 'exclude':
			return d[(d.line==1)&(d.direction==direction)&(d.drive1_percentage<=drive1_threshold)].reset_index()

		elif ramp == 'include':
			return d[(d.direction==direction)&(d.drive1_percentage<=drive1_threshold)].reset_index()

		elif ramp == 'only':
			return d[(d.line==0)&(d.direction==direction)&(d.drive1_percentage<=drive1_threshold)].reset_index()

		else:
			raise AttributeError('ramp options: exclude, include or only')

def mask(d,key,value):
    return d[d[key]==value]

def cvtime(a):
    b,c = a.split(':')
    return int(b)#datetime.time(int(b),int(c),0)


#make a dictionary for dummy variable
def dummy_dict(hd):
    dc ={}
    for ind, i in enumerate(sorted(set(hd))):
        dc[i] = ind
    return dc

#generators for clean data
def intordrop(s):
    try:
        return int(s)
    except ValueError:
        return np.nan

def clean(df):
    #drop useless kp
    df=df.loc[(df['kp']<700) & (df['status']!='Nan'),:]
    df.loc[:,'d_kp']=df['d_kp'].apply(intordrop)
    df=df.loc[df['d_kp'].notnull(),:]
    #deal with mix dtype
    df.loc[:,'status']=df['status'].astype(int)

    return df

from bokeh.io import show,output_notebook,output_file,save
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, LogColorMapper,HoverTool
from bokeh.palettes import Viridis256
from bokeh.plotting import figure

def corr_heatmap(df,output_html):
    df_corr = df.corr().unstack().reset_index()
    df_corr.columns=['x','y','corr']
    
    toolbar = 'hover,save,pan,box_zoom,reset,wheel_zoom'
    source =  ColumnDataSource(df_corr)
    mapper = LinearColorMapper(palette=Viridis256,high=1,low=-1)
    p = figure(tools=toolbar,toolbar_sticky=False,x_range=df_corr.x.unique(),y_range=df_corr.y.unique())
    p.rect(x='x',y='y',width=1,height=1,source=source, fill_color={'field':'corr','transform':mapper},line_color=None)
    colorb = ColorBar(color_mapper=mapper,location=(0,0))
    p.add_layout(colorb,'right')
    p.xaxis.major_label_orientation = 45
    
    hover = p.select_one(HoverTool)
    hover.tooltips = [('feature_0','@x'),("feature_1","@y"),("corr","@corr")]
    
    output_file(output_html)
    save(p)

