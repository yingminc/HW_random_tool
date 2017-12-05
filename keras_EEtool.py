import pandas as pd
import numpy as np
from sklearn import preprocessing
from keras.models import Sequential, load_model
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import Embedding
from keras.layers import Reshape
from keras.layers import Merge
from keras.layers import Activation
from keras.callbacks import ModelCheckpoint
import pickle
from util import *
import os

def embeddinglayer(feature, class_num, embedding_vec):
	model_= Sequential()
	model_.add(Embedding(class_num, embedding_vec,input_length=1))
	model_.add(Reshape(target_shape=(embedding_vec,)))

	for layer in model_.layers:
		layer.name = layer.name.split('_')[0]+'_'+feature

	return model_

def nonembeddinglayer(feature):
	#dense layer with 1 node; nothing change
	model_ = Sequential()
	model_.add(Dense(1,input_dim=1))
	for layer in model_.layers:
		layer.name = layer.name.split('_')[0]+'_'+feature

	return model_


def input_layer(ems, dict_emfeatures,nems):

	#set embedding layers
	layer1=[]
	for em in ems:
		cat, vec = dict_emfeatures[em]
		model_= embeddinglayer(em, cat, vec)
		layer1.append(model_)

	#set dense layers for numberic features
	for nem in nems:
		model_ = nonembeddinglayer(nem)
		layer1.append(model_)

	return layer1 #the first layer of NN
