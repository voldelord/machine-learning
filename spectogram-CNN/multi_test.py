import os
import glob
import sys
import progressbar
import numpy as np
from scipy.io import wavfile
import scipy
from matplotlib import mlab
import math
import keras
import random
from keras.models import load_model
from keras import backend as K 
from tensorflow import Session
import getbatch_binary as getbatch

label_set = [x[1] for x in os.walk("data/")][0]
label_set = sorted(label_set)

THRESHOLD = 0.5

def determineOptimalThreshold(groundTmean, groundFmean):
	f = 0
	best_TP = -1;
	best_FP = -1;
	best_TN = -1;
	best_FN = -1;
	best_thresh = 0
	for t in np.linspace(0.1,.9,81):
		TP = sum(1 for x in groundTmean if x >= t)
		FN = len(groundTmean) - TP
		FP = sum(1 for x in groundFmean if x >= t)
		TN = len(groundFmean) - FP

		precision = 0;
		recall = 0;

		if(FP == 0):
			precision = 1.0
		else:
			precision = TP / (TP + FP)
			

		if(FN == 0):
			recall = 1.0
		else:
			recall = TP / (TP + FN)
			
		score = precision * recall;
		if (score > f):
			best_TP = TP;
			best_FP = FP;
			best_TN = TN;
			best_FN = FN;
			best_thresh = t
			f = score 

	precision = best_TP / (best_TP + best_FP)
	recall = best_TP / (best_TP + best_FN)
	print(best_thresh)
	print("Precision: " +str(precision))
	print("Recall: " +str(recall))
	print("F1: " + str(2*(precision*recall)/(precision+recall)))

	return best_thresh

def getinput(file_name, Nsamp = 100):
	(sample_rate, signal) = wavfile.read(file_name)

	Nsamp = min(math.floor(signal.shape[0]/44100), Nsamp) 

	mono = signal.sum(axis = 1) / 2

	mean = np.mean(mono) # is about zero
	stddev = np.std(mono)
	if stddev == 0:
		stddev = 1

	mono = (mono - mean) / stddev

	IMSIZE = 128

	inputs = np.zeros((int(Nsamp), IMSIZE, IMSIZE))


	for i in range(Nsamp) :
		subsample = mono[(i*44100):(i+1)*44100]

		spec = mlab.specgram(subsample, Fs = 44100)[0]

		spec = scipy.misc.imresize(spec, [IMSIZE,IMSIZE])

		inputs[i,:,:] = spec
	
	return inputs


directory = 'testing/'

sample_files = glob.glob("testing/*.wav", recursive = True)

model_files = glob.glob("models/*.model", recursive = True)

model = []

for m in range(len(model_files)):
	del model
	K.clear_session()

	model = load_model(model_files[m])

	label = model_files[m].split("/")[1]
	label = label.replace('.model','')

	print(label)

	meanGround = []
	meanFalse = []

	sumG = 0
	sumF = 0
	Gcount = 0
	Fcount = 0

	TP = 0
	FP = 0
	TN = 0
	FN = 0

	for idx in progressbar.progressbar(range(len(sample_files))): 
		wav_file = sample_files[idx]

		txt_file=wav_file.replace(".wav",".txt")

		f = open(txt_file,"r")

		labels = f.read().splitlines()


		for i in range(len(labels)):
			labels[i] = ''.join(labels[i].split())

		input = getinput(wav_file)

		predictions = model.predict(input)

		mean = np.mean(predictions)
		prediction = mean > THRESHOLD
		ground_truth = label in labels

		if ground_truth:
			sumG += mean
			Gcount += 1
			meanGround.append(mean)
		else:
			sumF += mean
			Fcount += 1
			meanFalse.append(mean)
		#	print(mean)

		correct = (prediction == ground_truth)

		if correct:
			if prediction:
				TP+=1
			else:
				TN+=1
		else:
			if prediction:
				FP+=1
			else:
				FN+=1

	print(sumG/Gcount)
	print(sumF/Fcount)

	print(label)
	determineOptimalThreshold(meanGround,meanFalse)





