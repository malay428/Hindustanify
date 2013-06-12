#! /usr/bin/python
import numpy
import os
import random
import sys
import time
import sys, pyechonest, yaml, json
from echonest.remix import audio,modify
from pyechonest import config


config.ECHO_NEST_API_KEY="KE3VARQVC26QKIGED"



########################## Global variables ##########################################
TablaStrokesPath={
'dhen': '/audio/tabla/171897__ajaysm__dhen-stroke.wav',
'dhec': '/audio/tabla/171898__ajaysm__dhec-stroke.wav',
'dhe': '/audio/tabla/171899__ajaysm__dhe-stroke.wav',
'dha': '/audio/tabla/171900__ajaysm__dha-stroke.wav',
'ka': '/audio/tabla/171901__ajaysm__ka-stroke.wav',
'ga': '/audio/tabla/171902__ajaysm__ga-stroke.wav',
'dhun': '/audio/tabla/171903__ajaysm__dhun-stroke.wav',
'dhin': '/audio/tabla/171904__ajaysm__dhin-stroke.wav',
'ta': '/audio/tabla/171905__ajaysm__na-stroke.wav',
'na': '/audio/tabla/171905__ajaysm__na-stroke.wav',
'kat': '/audio/tabla/171906__ajaysm__kat-stroke.wav',
're': '/audio/tabla/171907__ajaysm__re-stroke.wav',
'ne': '/audio/tabla/171908__ajaysm__ne-stroke.wav',
'tun': '/audio/tabla/171909__ajaysm__tun-stroke.wav',
'tak': '/audio/tabla/171910__ajaysm__tak-stroke.wav',
'tin': '/audio/tabla/171911__ajaysm__tin-stroke.wav',
'tit': '/audio/tabla/171912__ajaysm__tit-stroke.wav',
'te': '/audio/tabla/171913__ajaysm__te-stroke.wav'}

TalaInfo = {
'teental': ['dha', 'dhin', 'dhin', 'dha', 'dha', 'dhin', 'dhin', 'dha', 'dha', 'tin', 'tin', 'ta', 'ta', 'dhin', 'dhin', 'dha']
}



def Hindustanify_main(inputfile, outputfile, tempoREDpc, tala):
  
  
	#reading tabla strokes files
	strokes={}
	for bol in TalaInfo[tala]:
		strokes[bol] = audio.AudioData(TablaStrokesPath[bol])
	
	#reading file and performning audio analsis
	audiofile = audio.LocalAudioFile(inputfile)
	
	#reading audio from drone file
	#C
	dronefile = audio.AudioData('drone_C.wav')
	#print "number of channels " + str(dronefile.numChannels)
	#dronefile = mono_to_stereo(dronefile)
	#print "number of channels " + str(dronefile.numChannels)
	dronefiledutation = dronefile.duration
	
	
	
	beats = audiofile.analysis.beats
	outputshape = (len(audiofile.data),)
	output = audio.AudioData(shape=outputshape, numChannels=1, sampleRate=44100)
	
	soundtouch = modify.Modify()
	drone_index=0
	
	for i, beat in enumerate(beats):
	    
	    #reading chunk of audio
	    data = audiofile[beat]
	    #slowing things down
	    new_audio_data = soundtouch.shiftTempo(audiofile[beat],tempoREDpc)

	    #reading drone chunk by chunk
	    drone_chunk = dronefile[drone_index:drone_index+ new_audio_data.data.shape[0]]
	    drone_index = drone_index + new_audio_data.data.shape[0]

	    # adding drone signal
	    new_audio_data = audio.mix(new_audio_data,drone_chunk, 0.5) 
	    
	    
	    #adding tabla strokes
	      

	    output.append(new_audio_data)
	    
	    
	    #check if the beat counter for drone might cross the drone duration
	    if drone_index > (dronefiledutation-(2*beat.duration))*dronefile.sampleRate:
			drone_index=0
			
	
	#for i, tatum in enumerate(audiofile.analysis.tatums):
	
	output.encode(outputfile)
	
	
def mono_to_stereo(audio_data):
    data = audio_data.data.flatten().tolist()
    new_data = numpy.array((data,data))
    audio_data.data = new_data.swapaxes(0,1)
    audio_data.numChannels = 2
    return audio_data
  
  
def tablaaudio(downbeatcnt, beatcnt, tatumcnt, taal):
	
	index = downbeatcnt*8 + beatcnt*2 + tatumcnt
	
	return taal[index]


