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
import essentia.standard as ess
import essentia as es
from mutagen.mp3 import MP3
from mutagen.mp3 import MPEGInfo
import numpy as np

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

    ### Important parameters
    AmplitudeFactorTablaStrokes = 0.55
    drone_mix_ratio = 0.2
    tabla_amp_factor = 0.8
    
    ### reading tabla strokes files
    strokes={}
    for bol in numpy.unique(TalaInfoFULL[taal]['normal']['bols'] + TalaInfoFULL[taal]['roll']['bols'] ):
        strokes[bol] = ess.MonoLoader(filename = TablaStrokesPath[bol])()

    # reading input file and performning audio analsis
    audio = ess.MonoLoader(filename = inputfile)()
    fs = MPEGInfo(open(inputfile)).sample_rate
    keyData = ess.KeyExtractor()(audio)
    key = notes[keyData[0]]
    mode = keyData[1]
    beatData = ess.RhythmExtractor2013()(audio)
    beats = beatData[1]
    beatConf = beatData[2]
    
    
    #based on the available drone files and the key and mode of the input audio files, determining what transpositino and which drone file should be used 
    get_drone_file, transposition_index = GetDroneFileandTransIndex(key, mode)
    droneAudio = ess.MonoLoader(filename = get_drone_file)()
    droneAudio = droneAudio## when transposed get that code here
    droneAudioLen = droneAudio.shape[0]

    #output files
    outputshape = audio.shape
    output  = np.zeros(outputshape, dtype=np.float32)
    outputTabla  = np.zeros(outputshape, dtype=np.float32)
    
    #looping over chunks of beats
    drone_index=0
    last_beat_loc = 0
    for ii in np.arange(len(beats)):
        
        strInd = np.floor(last_beat_loc*fs)
        endInd = np.floor(beats[ii]*fs)-1

        #reading chunk of audio
        data = audio[strInd:endInd]
        new_audio_data = data #when stretched, put that code here

         
        #reading drone chunk by chunk
        drone_chunk = droneAudio[drone_index:drone_index+ new_audio_data.shape[0]]
        drone_index = drone_index + new_audio_data.shape[0]

        # adding drone signal
        output[strInd:endInd] = new_audio_data*(1-drone_mix_ratio) + drone_chunk*drone_mix_ratio

        #check if the beat counter for drone might cross the drone duration
        if drone_index > droneAudioLen*0.8:
            drone_index=0
        last_beat_loc = beats[ii]
    
    
    generateTablaTrack(outputTabla,beats[::4], taal, strokes, fs)        

    output = output+ outputTabla*tabla_amp_factor
    ess.MonoWriter(filename = 'outputTrack.mp3', format = 'mp3', sampleRate = fs)(output)
    

def generateTablaTrack(output, bars, taal, strokes, fs):

    for ii,bar in enumerate(bars[:-1]):
        barLen = bars[ii+1]-bar
        for jj, bol in enumerate(TalaInfoFULL[taal]['normal']['bols']):
            startInd = np.floor((bar + barLen*TalaInfoFULL[taal]['normal']['durratio'][jj])*fs)
            lenStroke = len(strokes[bol])
            output[startInd: startInd+lenStroke] = output[startInd: startInd+lenStroke] + strokes[bol]

def GetDroneFileandTransIndex(key, mode):
    abs_diff = numpy.abs(DroneScales-key)
    index = numpy.argmin(abs_diff)
    
    transposition = key-DroneScales[index]
    print  Dronefiles[DroneNotes[index]], transposition
    return Dronefiles[DroneNotes[index]], transposition
    

    
if __name__=="__main__":
  
      # Python script to transform an audio song into a Hindustani music piece :D
      # arguments:
      # <pythonfile><inputaudio><outputaudio><tempofactor(1 = no change)><taal(rhythm cycle)>
      
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
    tempoREDpc = sys.argv[3]
    taal = sys.argv[4]
    
    Hindustanify_main(inputfile, outputfile, float(tempoREDpc), taal)
    
  

