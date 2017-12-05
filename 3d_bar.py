# -*- coding: utf-8 -*-
from __future__ import division
import pandas as pd

import datetime
import numpy as np

import argparse

parser =argparse.ArgumentParser()
parser.add_argument('highway',help = 'the desired highway; chose from: all, D1110, D1800, D214H', type=str)
parser.add_argument('direction',help = 'the desired highway; chose from: 2, 3, 4, 5', type=int)
parser.add_argument('--bar',help = 'make bar chart; default: line chart', action='store_true')
parser.add_argument('--show',help = 'show the plot', action='store_true')
parser.add_argument('--save',help = 'save png file', action='store_true')
args = parser.parse_args()


def mask(d,key,value):
	return d[d[key]==value]
def cvtime(a):
	b,c = a.split(':')
	return int(b)#datetime.time(int(b),int(c),0)


#make dictionary for dummy variable
def dummy_dict(hd):
	dc ={}
	for ind, i in enumerate(sorted(set(hd))):
		dc[i] = ind
	return dc

def make_3dbar(figurename, data, x_column, y_column, z_column, show=True, savepng=False):

	if show and savepng:
		raise ValueError('savepng and show cannot be both True')

	import matplotlib
	if savepng:
		matplotlib.use('Agg')
	else: 
		pass
	import matplotlib.pyplot as plt
	from matplotlib import cm
	import matplotlib.ticker
	from mpl_toolkits.mplot3d import Axes3D

	#take care of missing data
	d= data.fillna(0)


	xdict = dummy_dict(d[x_column])
	x = [xdict[i] for i in list(d[x_column])]
	xr = [ind for ind, i in enumerate(sorted(set(d[x_column])))]
	xlab = sorted(set(d[x_column]))



	yr = sorted(set(d[y_column]))
	#xr = sorted(set(d[x_column]))



	#set the figure
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	#set the color
	c0 = ['r','orange','y', 'g', 'c','b', 'm']
	c1 = c0*int(len(yr)/7)+c0[:(len(yr)%7)]

	print len(c1)

	#draw bar chart one lane by one lane
	
	for c, y in zip(c1, yr):
		xs = list(xr)
		ys = d[d[y_column]==y][z_column]#da[k]
		print y
		# You can provide either a single color or an array. To demonstrate this,
		# the first bar of each set will be colored cyan.
		cs = [c] * len(xs)
		ax.bar(xs, ys, zs=y, zdir='y', color=cs, alpha=0.7)

	#set axises
	#ax.xaxis.set_tick_params(pad = 12)
	#dplot.xaxis.set_ticks(xr)
	#ax.xaxis.set_ticklabels(xlab)

	ax.yaxis.set_ticks(yr)
	ax.yaxis.set_ticklabels(yr)
	ax.set_xlabel(x_column)
	#ax.set_ylabel(yr)
	ax.set_zlabel(z_column)
	ax.text2D(0.05, 0.09,figurename,transform = ax.transAxes)

	if savepng:
		print 'save'
		plt.savefig('{}.png'.format(figurename))
	if show:
		print 'show'
		plt.show()

def make_3dline(figurename, data, x_column, y_column, z_column, show=True, savepng=False):

	import matplotlib
	if savepng:
		matplotlib.use('Agg')
	else: 
		pass

	import matplotlib.pyplot as plt
	from mpl_toolkits.mplot3d import Axes3D

	#take care of missing data
	d= data.fillna(0)


	xdict = dummy_dict(d[x_column])
	x = [xdict[i] for i in list(d[x_column])]
	#xr = [ind for ind, i in enumerate(sorted(set(d[x_column])))]
	xlab = sorted(set(d[x_column]))

	yr = sorted(set(d[y_column]))
	xr = sorted(set(d[x_column]))


	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	print len(xr)


	#set the color
	c0 = ['r','orange','y', 'g', 'c','b', 'm']
	c1 = c0*int(len(yr)/7)+c0[:(len(yr)%7)]

	for c, y in zip(c1,yr): 
		print y
		zs = list(d[d[y_column]==y][z_column])
		ax.plot(xr, [y]*len(xr), zs, color = c)

	ax.yaxis.set_ticks(yr)
	ax.yaxis.set_ticklabels(yr)
	ax.set_xlabel(x_column)
	#ax.set_ylabel(yr)
	ax.set_zlabel(z_column)
	ax.text2D(0.05, 0.09,figurename,transform = ax.transAxes)

	if savepng:
		print 'save'
		plt.savefig('{}_line.png'.format(figurename))
	elif show:
		print 'show'
		plt.show()

	else:
		print('please specify if you want show the plot(--show) or save it as png(--save)')






highway=args.highway

direction = args.direction

feature = 'drive1:speed'


d = pd.read_csv('/run/user/1002/gvfs/smb-share:server=192.168.1.86,share=data/projects/Highway/NEXCO_2017/1_data/data_profiling/yearly_trends/yearly_trend_kp/{}_{}_yearly_trend_kp.csv'.format(highway,direction),header=0)

if args.bar:
	make_3dbar('{}_{}_yearly_trend'.format(highway,direction), d, 'kp', 'year', feature, show=args.show, savepng=args.save)


else:	
	make_3dline('{}_{}_yearly_trend'.format(highway,direction), d, 'kp', 'year', feature, show=args.show, savepng=args.save)
