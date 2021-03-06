#!project_pispeak/bin/python

import requests
import psutil
import re
import subprocess
import os
import sox
import math
import time
from gtts import gTTS
from configimport import *

def cancelAudio():
    bashCommand = 'killall mplayer & killall mpg123'
    subprocess.call(bashCommand, shell=True)
	
def getCpu():
    cpu_pct = psutil.cpu_percent(interval=1, percpu=False)
    cputemp = str(subprocess.check_output(['vcgencmd','measure_temp']))[7:11]
    print(cputemp)
    return(cpu_pct, cputemp)	

def getRam():
    mem = psutil.virtual_memory()
    mem_pct = mem.percent
    return(mem_pct)
	
def getSongs(commandText):
    pagelen = 25
    page = [int(s) for s in commandText.split() if s.isdigit()]
    if page:
        pass
    else:
        page = [1]
    pend = (page[0] * pagelen) -1
    pstart = pend - (pagelen -1)
    aud = os.listdir("/home/pi/audio/")
    aud = sorted(aud, key=str.lower)
    pages = math.floor(len(aud)/pagelen)
    pages = int(pages)
    partpage = len(aud) % pagelen
    if partpage > 0:
        pages += 1
    bank = '*Page ' + str(page[0]) + ' of ' + str(pages) +':*\n'
    for x,y in enumerate(aud):
        if x >= pstart and x <= pend:
            bank = bank + str(y) + '\n'
    text="*There are "+str(len(aud))+" available audio files.*\n"+bank
    return(text)

def logme(mess):
    f = open(pilogfile, "a")
    f.write(mess)
    f.close()
	
def play(song):
    toplay = song.replace('/play', '')
    toplay = toplay.replace('/p', '')
    toplay = toplay.lstrip()
    if re.match(r'.*(.mp3).*', toplay, re.IGNORECASE):
        bashCommand = 'mpg123'
    else:
        bashCommand = 'mplayer'
    bashCommand = bashCommand + ' /home/pi/audio/"'+toplay+'" &'
    subprocess.call(bashCommand, shell=True)

def postSay(commandText):
    words = commandText
    words = words.replace('/say', '')
    words = words.replace('/speak','')
    words = words.replace('/stop', '')
    words = words.replace('/s', '')
    words = words.replace('"', '')
    words = words.lower()
    swearFile = open('swearjar.txt','r')
    swearJar = swearFile.readlines()
    for i in range(len(swearJar)):
        swearJar[i] = swearJar[i].strip()
    swearFile.close()
    for s in swearJar:
        words = words.replace(s, 'beep')
    lang = 'en-us'
    langs=['au', 'ca', 'gb', 'gh', 'ie', 'in', 'ng', 'nz', 'ph', 'tz', 'uk', 'us', 'za', 'en', 'jp']
    if len(words.split('/')) > 1:
        lang = words.split('/')[1][:2]
        if lang in langs:
            lang = 'en-'+lang

    for l in langs:
        words = words.replace(l,'')
    words = words.replace('/', '').strip()
    print (words)
    tts = gTTS(words,lang=lang)
    tts.save('temp.mp3')

    bashCommand = 'mpg123 temp.mp3 && rm temp.mp3 &'
    subprocess.call(bashCommand, shell=True)

	
def postSong(filetype, url, audioname):
    if re.match(r'(mp3|wav)', filetype, re.IGNORECASE):
        audiofile = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
        open(audiofilepath+audioname, 'wb').write(audiofile.content)
        idealsound = float(.035)
        app = sox.Transformer()
        filebank = os.listdir(audiofilepath)
        for f in filebank:                                                         #modify any loud files so that they are quieter
            mean = app.stat(audiofilepath+f)['Mean norm']
            mean = float(mean)
            if mean > idealsound:
                percent = idealsound/mean
                bashCommand = 'sox -v ' + str(percent) + ' "' + audiofilepath + f + '" "' + audiotopath + f + '" && rm "' + audiofilepath + f + '" &'
                subprocess.call(bashCommand, shell=True)
            else:
                bashCommand = 'mv "' + audiofilepath + f + '" "' + audiotopath +'" &'
                subprocess.call(bashCommand, shell=True)

def searchSongs(searchString):
    returnArr = []
    returnStr = ''
    searchString = searchString.replace('/search','').strip()
    files = os.listdir("/home/pi/audio")
    files = sorted(files, key=str.lower)
    for f in files: 
        if re.search(searchString, f, re.IGNORECASE):
            returnArr.append(f)
    for f in returnArr:
        returnStr = returnStr+f+'\n'
    if (len(returnArr) < 1):
        returnStr = 'No results found. :disappointed_relieved:'
    return(returnStr)


