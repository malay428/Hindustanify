#!/usr/bin/python

import numpy
import os, sys
from copy import copy, deepcopy
import random
import sys
import time
import sys, pyechonest, yaml, json
from echonest.remix import audio,modify
from pyechonest import config
import math

config.ECHO_NEST_API_KEY="KE3VARQVC26QKIGED"

########################## Global variables ##########################################
TablaStrokesPath={
'dhen': 'audio/tabla/171897__ajaysm__dhen-stroke.wav',
'dhec': 'audio/tabla/171898__ajaysm__dhec-stroke.wav',
'dhe': 'audio/tabla/171899__ajaysm__dhe-stroke.wav',
'dha': 'audio/tabla/171900__ajaysm__dha-stroke.wav',
'ka': 'audio/tabla/171901__ajaysm__ka-stroke.wav',
'ga': 'audio/tabla/171902__ajaysm__ga-stroke.wav',
'dhun': 'audio/tabla/171903__ajaysm__dhun-stroke.wav',
'dhin': 'audio/tabla/171904__ajaysm__dhin-stroke.wav',
'ta': 'audio/tabla/171905__ajaysm__na-stroke.wav',
'na': 'audio/tabla/171905__ajaysm__na-stroke.wav',
'kat': 'audio/tabla/171906__ajaysm__kat-stroke.wav',
're': 'audio/tabla/171907__ajaysm__re-stroke.wav',
'ne': 'audio/tabla/171908__ajaysm__ne-stroke.wav',
'tun': 'audio/tabla/171909__ajaysm__tun-stroke.wav',
'tak': 'audio/tabla/171910__ajaysm__tak-stroke.wav',
'tin': 'audio/tabla/171911__ajaysm__tin-stroke.wav',
'tit': 'audio/tabla/171912__ajaysm__tit-stroke.wav',
'te': 'audio/tabla/171913__ajaysm__te-stroke.wav'}

Dronefiles ={
'D': 'audio/drone/155480__sankalp__electronic-tanpura-12.wav',
'E': 'audio/drone/155485__sankalp__electronic-tanpura-15.wav',
'F#': 'audio/drone/155489__sankalp__electronic-tanpura-18.wav',
'A': 'audio/drone/155494__sankalp__electronic-tanpura-6.wav',
'C': 'audio/drone/155500__sankalp__electronic-tanpura-3.wav'
}
DroneScales = numpy.array([2, 4 ,6 ,9 ,0])
DroneNotes = ['D','E','F#','A','C']

TalaInfo = {
'teental': ['dha', 'dhin', 'dhin', 'dha', 'dha', 'dhin', 'dhin', 'dha', 'dha', 'tin', 'tin', 'ta', 'ta', 'dhin', 'dhin', 'dha'],
'keherwa': ['dha', 'ga', 'na', 'te', 'na', 'ka', 'dhin', 'na', 'ta'],
'bhajan': ['dhin', 'ta', 'dhin', 'dhin', 'ta', 'tin', 'ta', 'tin', 'tin', 'ta', 'dha']
}

TalaInfoFULL = {
'teental': {'normal':{'bols':['dha', 'dhin', 'dhin', 'dha', 'dha', 'dhin', 'dhin', 'dha', 'dha', 'tin', 'tin', 'ta', 'ta', 'dhin', 'dhin', 'dha'],
			'durratio':[0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375]},
			'roll': {'bols':['dha', 'dhin', 'dhin', 'dha', 'dha', 'dhin', 'dhin', 'dha', 'dha', 'tin', 'tin', 'ta', 'ta', 'dhin', 'dhin', 'dha'],
			'durratio':[0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375]}},
'keherwa': {'normal':{'bols':['dha', 'ga', 'na', 'te', 'na', 'ka', 'dhin', 'na'],
			'durratio':[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]},
			'roll': {'bols':['dha', 'dhin', 'ta', 'dha', 'dhin', 'ta', 'dha', 'dhin', 'ta'],
			'durratio':[0.0, 0.0625, 0.1875, 0.3125, 0.375, 0.5, 0.625, 0.6875, 0.8125]}},
'bhajan': {'normal':{'bols':['dhin', 'ta', 'dhin', 'dhin', 'ta', 'tin', 'ta', 'tin', 'tin', 'ta'],
			'durratio':[0.0, 0.125, 0.1875, 0.3125, 0.375, 0.5,  0.625, 0.6875,  0.8125, 0.875]},
			'roll': {'bols':['dha', 'dhin', 'ta', 'dha', 'dhin', 'ta', 'dha', 'dhin', 'ta'],
			'durratio':[0.0, 0.0625, 0.1875, 0.3125, 0.375, 0.5, 0.625, 0.6875, 0.8125]}}
}

notes = {'C':0, 'C#':1,'D':2,'D#':3,'E':4, 'F':5, 'F#':6, 'G':7,'G#':8,'A':9,'A#':10,'B':11}


def Hindustanify_main(inputfile, outputfile, tempoREDpc, taal):

	soundtouch = modify.Modify()
  
	### Important parameters
	AmplitudeFactorTablaStrokes = 0.4
    
  
	### reading tabla strokes files
	strokes={}
	for bol in numpy.unique(TalaInfoFULL[taal]['normal']['bols'] + TalaInfoFULL[taal]['roll']['bols'] ):
		strokes[bol] = audio.AudioData(TablaStrokesPath[bol])
		strokes[bol].data = AmplitudeFactorTablaStrokes*strokes[bol].data[:,0]
		strokes[bol].numChannels = 1	
	
    
	# reading input file and performning audio analsis
	audiofile = audio.LocalAudioFile(inputfile)
	key = audiofile.analysis.key['value']
	mode = audiofile.analysis.mode['value']
    
	get_drone_file, transposition_index = GetDroneFileandTransIndex(key, mode)
	
	#reading audio from drone file
	#C
	dronefile = audio.AudioData(get_drone_file)
	dronefile.data = dronefile.data[:,0]
	dronefile.numChannels =1
	dronefile = soundtouch.shiftPitchSemiTones(dronefile, transposition_index)
	
	#print "Drone file read"
	#print "number of channels " + str(dronefile.numChannels)
	#dronefile = mono_to_stereo(dronefile)
	#print "number of channels " + str(dronefile.numChannels)
	dronefiledutation = dronefile.duration
    
	beats = audiofile.analysis.beats
	outputshape = (len(audiofile.data),)
	output = audio.AudioData(shape=outputshape, numChannels=1, sampleRate=44100)
	final_out = audio.AudioData(shape=outputshape, numChannels=1, sampleRate=44100)
    

	drone_index=0
    
	for i, beat in enumerate(beats):
	    
		#if beat.end > audiofile.duration/6:
			#tempoREDpc=1
		#reading chunk of audio
		data = audiofile[beat]
		#slowing things down
		new_audio_data = soundtouch.shiftTempo(audiofile[beat],tempoREDpc)

		#reading drone chunk by chunk
		drone_chunk = dronefile[drone_index:drone_index+ new_audio_data.data.shape[0]]
		drone_index = drone_index + new_audio_data.data.shape[0]

		# adding drone signal
		new_audio_data = audio.mix(new_audio_data,drone_chunk, 0.7) 

		output.append(new_audio_data)
	    
	    
		#check if the beat counter for drone might cross the drone duration
		if drone_index > (dronefiledutation-(2*beat.duration))*dronefile.sampleRate:
			drone_index=0
	
	output = AddTabla(output,audiofile.analysis.bars, audiofile.analysis.sections, tempoREDpc, taal, strokes)		
	'''print "started tabla strokes addition"
	for i, tatum in enumerate(audiofile.analysis.tatums[2:-1]):
		
		onset = (tatum.end - tatum.duration)
		print onset
		print type(strokes[tablaaudio2(i,taal)])
		output.add_at(onset,strokes[tablaaudio2(i,taal)])
		'''
	
	output.encode(outputfile)

def AddTabla(audiodata, bars, sections, tempofactor, taal, strokes):
	
	if tempofactor <=0.5:
		New_bars = [None]*(len(bars) + len(bars))
		New_bars[::2] = deepcopy(bars)
		New_bars[1::2] = deepcopy(bars)
	
		for i,bar in enumerate(New_bars):
			
			if i%2 ==0:
				New_bars[i].duration= New_bars[i].duration/2
			else:
				New_bars[i].start = New_bars[i-1].start + New_bars[i-1].duration
				New_bars[i].duration = New_bars[i].duration/2
				
		bars = deepcopy(New_bars)
	
	if taal == 'teental':

		for i,bar in enumerate(bars):
			if i%2 == 0:
				bar_onset = bar.start/tempofactor
				bar_duration = bar.duration/tempofactor
			if i%2 ==1:
				bar_duration = bar_duration + (bar.duration/tempofactor)
				for j, bol in enumerate(TalaInfoFULL[taal]['normal']['bols']):
					audiodata.add_at(bar_onset + (bar_duration*TalaInfoFULL[taal]['normal']['durratio'][j]) ,strokes[bol])
			
	else:
		section_cnt =0 ;
		for i,bar in enumerate(bars):
			section_offset = sections[section_cnt].start + sections[section_cnt].duration
			if bar.end >= section_offset:
				#print "hello"
				play_roll =1
				section_cnt = section_cnt+1
			else:
				play_roll = 0
			bar_onset = bar.start/tempofactor
			bar_duration = bar.duration/tempofactor
			
			if play_roll ==0:
				for j, bol in enumerate(TalaInfoFULL[taal]['normal']['bols']):
					audiodata.add_at(bar_onset + (bar_duration*TalaInfoFULL[taal]['normal']['durratio'][j]) ,strokes[bol])
			else:
				for j, bol in enumerate(TalaInfoFULL[taal]['roll']['bols']):
					audiodata.add_at(bar_onset + (bar_duration*TalaInfoFULL[taal]['roll']['durratio'][j]) ,strokes[bol])
			

	return audiodata
	
		
def tablaaudio2(tatumcnt, taal):
	
	index = numpy.mod(tatumcnt, len(TalaInfo[taal]))

	return TalaInfo[taal][index]
      
      
def mono_to_stereo(audio_data):
	data = audio_data.data.flatten().tolist()
	new_data = numpy.array((data,data))
	audio_data.data = new_data.swapaxes(0,1)
	audio_data.numChannels = 2
	return audio_data
  
  
def tablaaudio(downbeatcnt, beatcnt, tatumcnt, taal):
	
	index = downbeatcnt*8 + beatcnt*2 + tatumcnt
	
	return TalaInfo[taal][index]
      

def GetDroneFileandTransIndex(key, mode):
	abs_diff = numpy.abs(DroneScales-key)
	index = numpy.argmin(abs_diff)
	
	transposition = key-DroneScales[index]
	
	return Dronefiles[DroneNotes[index]], transposition
	

def AddGamakas(inputfile, outputfile):

	soundtouch = modify.Modify()
  
  	# reading input file and performning audio analsis
	audiofile = audio.LocalAudioFile(inputfile)
	key = audiofile.analysis.key['value']
	mode = audiofile.analysis.mode['value']
    
	beats = audiofile.analysis.beats
	outputshape = (len(audiofile.data),)
	output = audio.AudioData(shape=outputshape, numChannels=1, sampleRate=44100)
	
	sr = audiofile.sampleRate
	wlen = 0.1
	framelen=int(math.floor(wlen*sr))
	nos = int(math.floor(audiofile.duration/wlen))
	
	for ii in range(0,nos):
		audiodata = audiofile[ii*framelen:(ii+1)*framelen,:]
		ratio = 2*math.sin(2*math.pi*ii*wlen*4)
		#print ratio
		new_data = soundtouch.shiftPitchSemiTones(audiodata, semitones = int(math.floor(ratio + 0.5)))
		output.append(new_data)
	
	output.encode(outputfile)
		
	
	
if __name__=="__main__":
  
	inputfile = sys.argv[1]
	outputfile = sys.argv[2]
	tempoREDpc = sys.argv[3]
	taal = sys.argv[4]
	
	Hindustanify_main(inputfile, outputfile, float(tempoREDpc), taal)
	
  

