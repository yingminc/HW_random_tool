
# coding: utf-8

# In[10]:

import pandas as pd

from bokeh.core.properties import field
from bokeh.io import curdoc,output_notebook
from bokeh.layouts import layout,widgetbox,row, column
from bokeh.models import (
    ColumnDataSource, HoverTool, SingleIntervalTicker, Slider,DateRangeSlider, Button, Label,#RelativeDelta,HBox,
    CategoricalColorMapper, Select, LinearAxis, Range1d
)
from bokeh.palettes import Spectral6
from bokeh.plotting import figure,show, output_file

from datetime import timedelta


# In[11]:

filecode='180015'
do = pd.read_csv('/media/yingminc/toshiba/pre_experiment/Embedding_test/30minappend_test_%s.csv'%filecode,header=0, usecols =[0,2,3,4,5,6] )


# In[12]:

d=do.loc[do['date']=='2015-12-30',:].copy()


# In[13]:

d=d.dropna(how='any').copy().reset_index()


# In[14]:

thr = 40
d.loc[d['speed']>40,'color'] = 'blue'
d.loc[d['speed']>40,'congection'] = 'speed>40'
d.loc[d['speed']<=40,'color'] = 'orange'
d.loc[d['speed']<=40,'congection'] = 'speed<=40'


# In[15]:

times = list(sorted(set(d['time'])))
time_dict = {ind: t for ind, t in enumerate(times)}


# In[16]:

data_dict={ind: d.loc[d['time']==t,:] for ind, t in enumerate(times) }

direction = list(set(d.direction))


# In[17]:

source = ColumnDataSource(data=data_dict[0])


# In[18]:

toolbar = 'pan,wheel_zoom,box_zoom,reset,hover,save'


# In[19]:

plot = figure(x_range =(0, max(d.kp)), y_range =(0, 200),output_backend='webgl',tools=toolbar)
plot.xaxis.axis_label = "kp"
plot.yaxis.axis_label = "speed"

plot.extra_y_ranges={'carv':Range1d(start=0, end=50)}

plot.add_layout(LinearAxis(y_range_name='carv',axis_label='car_volumn'),'right')

label = Label(x=3, y=150, text=time_dict[0], text_font_size='80pt', 
              text_alpha = 0.3,text_color='#%02x%02x%02x' %(int(0*0.8), int(255-0*0.8), 150) )

plot.add_layout(label)


# In[20]:

plot.circle('kp','speed', source=source, size ='car_volumn', legend='congection',
            fill_alpha=0.3 , fill_color ='color',line_alpha = 1, line_color=None)


# In[21]:

#plot = figure(x_range =(0, 35), y_range =(0, 100),output_backend='webgl',tools='hover')
plot.vbar('kp',0.5,0,'car_volumn',source = source, legend='car volumn',
          fill_color = 'red', fill_alpha = 0.1, line_color =None)


# In[22]:

def anime_update():
    time_ind = slider.value+1
    if time_ind > 287:
        time_ind = 0
    slider.value = time_ind


# In[23]:

def data_update(attrname, old, new):
    time_ind = slider.value
    label.text = str(time_dict[time_ind])
    label.text_color = '#%02x%02x%02x' %(int(time_ind*0.8), int(255-time_ind*0.8), 150)
    if select.value=='both':
        dd = d
    elif select.value==str(direction[0]):
        dd =d.loc[d['direction']==direction[0],:]
    else:
        dd =d.loc[d['direction']==direction[1],:]
    source.data = dict(dd.loc[dd['time']==time_dict[time_ind],:])


# In[24]:

slider = Slider(start = 0, end = 287, value = 0,title= 'time',step =1)
slider.on_change('value',data_update)


# In[25]:

def anime():
    if button.label == 'play':
        button.label = 'pause'
        curdoc().add_periodic_callback(anime_update,300)
    else:
        curdoc().remove_periodic_callback(anime_update)
        button.label = 'play'


# In[26]:

button = Button(label='play', width=60)
button.on_click(anime)


# In[27]:

select = Select(options=['both',str(direction[0]),str(direction[1])],title='direction')
select.on_change('value',data_update)


# In[28]:

hover = plot.select_one(HoverTool)
hover.point_policy ="follow_mouse"
hover.tooltips = [('kp','@kp'),('direction','@direction'),('speed',"@speed"),('car volumn','@car_volumn')]


# In[29]:

w = widgetbox([slider,button,select])
h = row(children=[plot,w])


# In[30]:

curdoc().add_root(h)
curdoc().title = 'Test'


# In[31]:

output_file('slider_test4.html')


# In[32]:

show(h)


# In[ ]:




# In[ ]:



