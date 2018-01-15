import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os




project_path = '/data/projects/Highway/NEXCO_2017/'

cols=['drive1_carvol','drive2_carvol','takeover_carvol','hill_carvol']

years = [i for i in range(2004,2018)]
highways =['D1800', 'D214H']
directions = {'D1110':[4,5], 'D1800':[2,3], 'D214H':[2,3]}

#os.mkdir(os.path.join(project_path,'2_visualization/error_heatmap/'))

for highway in ['D1800']:
	os.mkdir(os.path.join(project_path,'2_visualization/error_heatmap/{}_swapkp'.format(highway)))
	for year in years:
		start = datetime(int(year),1,1,0,0)
		end = datetime(int(year)+1,1,1,0,0)
		delta = end-start
		span = [start+timedelta(seconds=i*5*60) for i in range(0,delta.days*288)]
		sd=pd.DataFrame(span)
		sd.columns=['datetime']
		sd['datetime'] = pd.to_datetime(sd['datetime'])
		sd['month']=sd.datetime.dt.month
		total_num=sd.groupby('month').count()['datetime']


		for direction in [2]:
			print highway,year,direction
			d=pd.read_csv(os.path.join(project_path,
				'1_data/engineered_data/road_status_filled_labeled/{}/{}_{}_direction{}.csv'.format(highway,highway,year,direction)),
				header = 0)
			d = d.replace({999:np.nan})
			d['datetime'] = pd.to_datetime(d['datetime'])
			d['day']=d.datetime.dt.day
			d['month']=d.datetime.dt.month
			d['year']=d.datetime.dt.year
			d2 = d[['month','kp']+cols].groupby(['month','kp']).count().unstack()
			dp = d2.div(total_num,axis=0)

			if highway=='D214H':
				dp['drive2_carvol'] = dp['drive2_carvol'].replace({0:-1})
				dp['hill_carvol'] = dp['hill_carvol'].replace({0:-1})
			else:
				if direction == 3:
					kp_nodrive2=[kp for kp in d.kp.unique() if (kp<0.7) or(kp>92.1)]
					kp_nohill=[kp for kp in d.kp.unique() if (kp<105.2) or(kp>112.6)]
				else:
					kp_nodrive2=[kp for kp in d.kp.unique() if (kp<1.3) or (kp>92.1)]
					kp_nohill=[kp for kp in d.kp.unique() if (kp<31.9) or ((kp>33.3) and 
						(kp<53.8)) or ((kp>55.2) and(kp<70)) or ((kp>71.6) and (kp<101.8)) or (kp>103.3)]
				dp.loc[:,('drive2_carvol',kp_nodrive2)]=dp.loc[:,('drive2_carvol',kp_nodrive2)].replace({0:-1})
				dp.loc[:,('hill_carvol',kp_nohill)]=dp.loc[:,('hill_carvol',kp_nohill)].replace({0:-1})

			fig, ax = plt.subplots(nrows=len(cols),figsize=(45,10*len(cols)))
			for ind, col in enumerate(cols):
				sns.heatmap(dp[col],annot=True,linewidth=0.5,ax=ax[ind],vmin=-1,vmax=1)
				ax[ind].set_title('{} valid data'.format(col))
				plt.suptitle('{}_{}_dir{}'.format(highway,year,direction),fontsize=25)
				plt.savefig(os.path.join(project_path,'2_visualization/error_heatmap/{}_swapkp/{}_{}_dir{}.png'.format(highway,highway,year,direction)))