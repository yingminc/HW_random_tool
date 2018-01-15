# coding: utf-8
import pandas as pd
import numpy as np
import os
from datetime import datetime
from datetime import timedelta


def spot_to_span(dtlist,gapseconds=60*5,fillseconds=60*0):
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
		if (span[1]-span[0]).total_seconds()>fillseconds:
			longspans.append(span)
	return longspans


highways = ['D1800','D214H']

years = ['20{:02d}'.format(i) for i in range(4,18)]
#years = ['2014']

directions = {'D1110':[4,5], 'D1800':[2,3], 'D214H':[2,3]}

lanes = ['drive1', 'drive2', 'takeover','hill']

features = ['carvol', 'bigcar','occ','speed']

all_cols = ['_'.join((lane, f)) for lane in lanes for f in features ]

folderpath = '/data/projects/Highway/NEXCO_2017/1_data/'

newc = ['highway_code', 'year', 'month', 'day','date','weekday','holiday','time','direction','kp','line','ramp',
	   'drive1_carvol','drive1_bigcar', 'drive1_occ','drive1_speed',
	  'drive2_carvol','drive2_bigcar', 'drive2_occ','drive2_speed',
	  'takeover_carvol','takeover_bigcar', 'takeover_occ','takeover_speed',
	  'hill_carvol','hill_bigcar', 'hill_occ','hill_speed','error']

#os.mkdir(os.path.join(folderpath,'data_profiling/error_list_fill_24hr'))

for highway in highways:
	for year in years:

		start = datetime(int(year),1,1,0,0)
		end = datetime(int(year)+1,1,1,0,0)
		delta = end-start
		span = [start+timedelta(seconds=i*5*60) for i in range(0,delta.days*288)]

		print len(span)

		for direction in directions[highway]:

			print highway, year, direction

			d = pd.read_csv(os.path.join(folderpath,'engineered_data/road_status/{}/{}_{}_direction{}.csv'.format(highway,highway,year,direction)), header=0,usecols=range(len(newc)))
			print('load data')

			#d.columns= newc

			d=d.replace({999:np.nan})

			#d['datetime'] = pd.to_datetime(d['date']+' '+d['time'])
			d['datetime'] = pd.to_datetime(d['date']+' '+d['time'])

			for lane in lanes:
				cols=['_'.join((lane, f)) for f in features[:-1]]
				d.loc[(d[cols]==0).all(axis=1),'_'.join((lane,'speed'))]=100

			error={}
			for kp in list(set(d.loc[d.line==1,'kp'])):
				print kp
				error[kp]={}
				dd = d.loc[d.kp==kp]
				timemissing = list(set(span).difference(set(dd.datetime)))
				if len(timemissing)>0:
					print 'missing_raw_data'
					error[kp]['missing_raw_data']=spot_to_span(timemissing, fillseconds=0)
				for lane in lanes:
					cols=['_'.join((lane, f)) for f in features]
					print 'check '+lane

					if dd[cols].isnull().values.all():
						print 'no_lane_'+lane
						error[kp]['no_lane_'+lane]=[(span[0],span[-1])]

					elif len(list(dd.loc[(dd[cols].isnull()).all(axis=1),'datetime']))>0: 
						#delete the one longer than 1 day (should be no error longer than oneday)
						print 'data_missing_'+lane
						print spot_to_span(list(dd.loc[dd[cols].isnull().all(axis=1),'datetime']))
						error[kp]['data_missing_'+lane]=spot_to_span(list(dd.loc[dd[cols].isnull().all(axis=1),'datetime']), fillseconds=0)

					for col in cols:
						if len(list(dd.loc[(dd[col].isnull())&(~dd[cols].isnull().all(axis=1)),'datetime']))>0:
								#fill with 0
							print 'data_missing_'+col
							error[kp]['data_missing_'+col]=spot_to_span(list(dd.loc[dd[col].isnull(),'datetime']), fillseconds=0)
			kpcol=[]
			lanecol=[]
			stcol=[]
			encol=[]
			for kp in error.keys():
				for col in error[kp].keys():
					for st, en in error[kp][col]:
						kpcol.append(kp)
						lanecol.append(col)
						stcol.append(st)
						encol.append(en)

			er=pd.DataFrame({'kp':kpcol, 'lane':lanecol, 'start':stcol,'end':encol})

			er['length']= (er.end-er.start)

			er['highway'] = highway

			er['year'] = year

			er['direction'] = direction

			er = er[['highway','year','direction','kp','lane','start','end','length']]

			#er.to_csv('test_err.csv',index=None)

			with open(os.path.join(folderpath,'data_profiling/error_list/{}_direction{}.csv'.format(highway,direction)),'a') as thecsv:
				if year == '2004':
					er.to_csv(thecsv,header=True, index=None)
				else:
					er.to_csv(thecsv,header=False, index=None)


