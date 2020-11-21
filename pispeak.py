#!project_pispeak/bin/python

import re
import math
import time
from datetime import datetime
import json
import requests
from slackclient import SlackClient

import functions
from functions import *
from configimport import *

slack_client = SlackClient(token)
user_list = slack_client.api_call("users.list")


for user in user_list.get('members'):
    if user.get('name') == botName:
        slack_user_id = user.get('id')
        break

if slack_client.rtm_connect():
    print ("Connected!")
    while True:
        for message in slack_client.rtm_read():
            if 'text' in message and message['text'].startswith("<@%s>" % slack_user_id):
                message_text = message['text']
                #logme ("Message json: %s \n" % json.dumps(message, indent=2))
                try:
                    message_user = message['user']
                    userRealName = slack_client.api_call("users.info", user=message_user)['user']['real_name']
                except:
                    pass
                try:
                    message_subtype = message['subtype']
                except:
                    pass
                try:
                    logme ("Message received: " + message_text[13:] + '\nFrom: ' + message_user + ' : ' + userRealName + '\nAt: '+datetime.strftime(datetime.now(), "%m/%d/%Y %I:%M %p")+'\n\n')
                except:
                    pass
                try:
                    if message_subtype == 'bot_message':                                        #Ignore Bot Messages!
                       logme ("Bot Message Ignored!\n\n")
                       break
                except: pass

                def refineMessage(words):
                    words = words.replace('<@'+slack_user_id+'>', '')
                    return (words)


                def slackReply(commandText):
                    slack_client.api_call(
                            "chat.postMessage",
                            channel=message['channel'],
                            text=commandText,
                            as_user=True)

                if re.match(r'.*(cpu).*', message_text, re.IGNORECASE):                         #CPU functionality
                    cpu_pct,cputemp = getCpu()
                    piCpu = "My CPU is at " + str(cpu_pct) + "% Running at " + cputemp + "°C"
                    slackReply(piCpu)

                if re.match(r'.*(memory|ram).*', message_text, re.IGNORECASE):                  #RAM/memory functionality
                    mem_pct = getRam()
                    piMem="My RAM is at %s%%." % mem_pct
                    slackReply(piMem)

                if re.search('/search', message_text, re.IGNORECASE):                           #Search Functionality
                    searchString = refineMessage(message_text)
                    slackReply(searchSongs(searchString))
 
                elif re.match(r'.*(/s|/say|/speak).*', message_text, re.IGNORECASE):            #Say command functionality
                    newMessage = refineMessage(message_text)
                    postSay(newMessage)

                elif re.match(r'.*(/u|/upload).*', message_text, re.IGNORECASE):                #upload functionality
                    filetype = message['files'][0]['filetype']
                    url = message['files'][0]['url_private_download']
                    audioname = message['files'][0]['name']
                    postSong(filetype, url, audioname)

                elif re.match(r'.*(/p|/play).*', message_text, re.IGNORECASE):                  #play existing file
                    newMessage = refineMessage(message_text)
                    play(newMessage)

                elif re.match(r'.*(/q|/stop|/shutup|/cancel|/end|/quiet|/quit).*', message_text, re.IGNORECASE):  #stop anything that is playing
                    cancelAudio()

                elif re.match(r'.*(/l|/list|/clips|/songs).*', message_text, re.IGNORECASE):    #list available audio files
                    reply = getSongs(message_text)
                    slackReply(reply)

                elif re.match(r'.*(/h|/help).*', message_text, re.IGNORECASE):                  #display help
                    helpFile = open('help.txt','r')
                    slackReply(helpFile.read())
                    helpFile.close()

        time.sleep(1)

