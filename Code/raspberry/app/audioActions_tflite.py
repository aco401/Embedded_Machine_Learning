import threading
from threading import Event
from defines_tflite import ActionsEvents, Topics, StateEvents
from pubsub import pub 
import pyaudio
import wave
import time
import sys
from collections import deque

class AudioActions(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.q = deque()
        #print("Init")
        pub.subscribe(self.notifyEvent, Topics.TOPIC_ACTIONS.value)
                
    # PubSub
    def notifyEvent(self, arg1):
    	#print("Tried to append an event")
    	self.q.append(arg1)
    	
    def run(self):
    	while(1):
    		if not(len(self.q) == 0):
    			#print("AudioActions started")
    			self.lookUpAudio(self.q.popleft())
    
    
    def lookUpAudio(self, arg1):
        print(arg1)
        if (arg1 == ActionsEvents.AUDIO_DRINK.value):
            self.playWAV(file="audio/please_drink.wav")
        elif (arg1 == ActionsEvents.AUDIO_CROOKED.value):
            self.playWAV(file="audio/straight_back_please.wav")
        elif (arg1 == ActionsEvents.AUDIO_NOPERSON.value):
            self.playWAV(file="audio/keep_working.wav")
        elif (arg1 == ActionsEvents.AUDIO_PHONE.value):
            self.playWAV(file="audio/phone.wav")
        elif (arg1 == ActionsEvents.AUDIO_WD_OPEN.value):
            self.playWAV(file="audio/open_window.wav")
            
    
            
    def playWAV(self, file='audio/i_will_be_back.wav'):
        p = pyaudio.PyAudio() # instantiate PyAudio (1)
        wf = wave.open(file, 'rb')

        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)

        # open stream using callback (3)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)
        
        # start the stream (4)
        stream.start_stream()

        # wait for stream to finish (5)
        while stream.is_active():
            time.sleep(0.1)

        # stop stream (6)
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate() # close PyAudio (7)


        

                
                
                


