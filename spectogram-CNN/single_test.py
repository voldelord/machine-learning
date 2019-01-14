import os
import glob
import sys
import progressbar
import numpy as np
from scipy.io import wavfile
import math
import keras
import random
from keras.models import load_model
from keras import backend as K 
from tensorflow import Session
import getbatch_binary as getbatch

label_set = getbatch.labels;

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

	inputs = np.resize(mono,Nsamp*44100).reshape(-1,44100)
	
	return inputs


# def getinput(file_name, nSamp = 100):
# 	(sample_rate, signal) = wavfile.read(file_name)
# 	mono = signal.sum(axis = 1) / 2

# 	mean = np.mean(mono) # is about zero
# 	stddev = np.std(mono)
# 	if stddev == 0:
# 		stddev = 1

# 	mono = (mono - mean) / stddev

# 	inputs = np.zeros((nSamp,44100))

# 	for i in range(nSamp):
# 		tmp = random.randint(0, len(mono)-44100 - 1)
# 		sample = mono[tmp:tmp+44100]
# 		#sample = mono[i*44100:(i + 1)*44100]
# 		inputs[i,:] = sample
	
# 	return inputs

directory = 'testing/'

sample_files = glob.glob("testing/*.wav", recursive = True)

model_files = glob.glob("models/*.model", recursive = True)

correct = 0;

model = load_model("multi_model/model.model")

for idx in progressbar.progressbar(range(len(sample_files))): 
	wav_file = sample_files[idx]

	txt_file=wav_file.replace(".wav",".txt")

	f = open(txt_file,"r")

	labels = f.read().splitlines()


	for i in range(len(labels)):
		labels[i] = ''.join(labels[i].split())

	input = getinput(wav_file)

	highestActivation = -1;
	bestGuess = -1;

	prediction = model.predict(input)

	summed = np.sum(prediction, axis = 0)

	best = np.argmax(summed)

	label = label_set[best]
	if label in labels:
		correct += 1

acc = correct / len(sample_files);
print("Accuracy: " + str(acc)) 




