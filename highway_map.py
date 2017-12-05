# -*- coding: utf-8 -*-
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool,LinearColorMapper,
    ColorBar, BoxSelectTool,HoverTool,ResetTool#,PreviewSaveTool
)
import pandas as pd
from bokeh.palettes import Viridis256

import argparse

parser =argparse.ArgumentParser()
parser.add_argument('filename', help = 'output html filename(no extension pls)',type=str)
parser.add_argument('highway',help = 'the desired highway; chose from: all, D1110, D1800, D214H', type=str)
args = parser.parse_args()

def highway_map(filename='map', highway='all'):

	#load th coordinates of all highways
	cod_all = pd.read_csv('./all_2_cod.csv', header=0)

	#load the facilities info of all highways
	fc_all = pd.read_csv('./fc_2_cod.csv', header=0)

	if highway == 'all':
		cod = cod_all
		fc = fc_all
		zoom_scale = 9

	elif highway == 'D1110':
		cod = cod_all[cod_all.highway_code == 'D1110'].copy()
		fc = fc_all[fc_all.highway_code == 'D1110'].copy()
		zoom_scale = 12

	elif highway == 'D1800':
		cod = cod_all[cod_all.highway_code == 'D1800'].copy()
		fc = fc_all[fc_all.highway_code == 'D1800'].copy()
		zoom_scale = 9

	elif highway == 'D214H':
		cod = cod_all[~cod_all.highway_code.isin(['D1110','D1800'])].copy()
		fc = fc_all[~fc_all.highway_code.isin(['D1110','D1800'])].copy()
		zoom_scale = 11

	else:
		print('Please chose highway from: all, D1110, D1800, D214H')

	#creat the basemap
	map_options = GMapOptions(lat=(cod.lat.mean()), lng=(cod.lon.mean()), map_type="roadmap", zoom=zoom_scale)

	plot = GMapPlot(
	    x_range = DataRange1d(), y_range = DataRange1d(), map_options=map_options,plot_height=900,plot_width=1500)

	plot.title.text = highway

	colormap = LinearColorMapper(palette=Viridis256, high=max(cod['h']),
	                                low = min(cod['h']))

	# For GMaps to function, Google requires you obtain and enable an API key:
	#
	#     https://developers.google.com/maps/documentation/javascript/get-api-key
	#
	# Replace the value below with your personal API key:

	plot.api_key = '{APIkey}'

	#draw highways and facilities
	source = ColumnDataSource(data=cod)
	fcsource = ColumnDataSource(data=fc)

	circle = Circle(x="lon", y="lat", size=5, fill_color={'field':'h', 'transform':colormap}, 
	                fill_alpha=0.1, line_color=None)

	fcircle=Circle(x="lon", y="lat", size=7, fill_color='red', 
	                fill_alpha=0.5,line_color=None)

	cc = plot.add_glyph(source, circle)
	fc = plot.add_glyph(fcsource, fcircle)

	plot.add_layout(ColorBar(color_mapper=colormap,location=(0,0)),'left')


	plot.add_tools(ResetTool(),PanTool(), WheelZoomTool(),
	               HoverTool(renderers=[cc,fc],tooltips= [('highway','@highway'),("kp","@kp"),('fc','@facility_name'),
	               	('direction','@direction')]))

	output_file("{}.html".format(filename))
	show(plot)

highway_map(args.filename, args.highway)
