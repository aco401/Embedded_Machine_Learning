from sys import argv, stderr, exit
from os import getenv
import os

import numpy as np
import tensorflow as tf
import tflite_runtime.interpreter as tflite
from tensorflow import keras
import time

import pygame
from Recording.camera_tflite import Camera
from pydub import AudioSegment
from pydub.playback import play

from statemachine import StateMachine, State
from defines_tflite import StateEvents, Topics, ActionsEvents
from pubsub import pub
import atexit
import threading
from log_to_graph import log_to_graph


class classificator(threading.Thread):
    
    def __init__(self, threadID, model_file, video, sendEvents, res=(128, 128)):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.model_file = model_file
        self.video = video
        self.sendEvents = sendEvents
        self.camera = Camera(training_mode=False, res=res)
        self.log_file = open('log_' + str(time.time()), 'a')
        atexit.register(self.hook)

    def hook(self):
        self.log_file.close()
        log_to_graph(self.log_file.name)
        os.remove(self.log_file.name)
        
    def throwEvent(self, topic, event):
        pub.sendMessage(topic, arg1=event)
        
    def convertToEvent(self, classname):
        if classname == 'crooked':
                self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.CROOKED.value)
        elif classname == 'drinking':
                self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.DRINKING.value)
        elif classname == 'noperson':
                self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.NOPERSON.value)
        elif classname == 'phone':
                self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.PHONE.value)
        elif classname == 'straight':
                self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.STRAIGHT.value)

    	
    def notifyEvent(self, event):
        if event == StateEvents.OK_SIGN.value:
            self.ok_sign()
        
    def run(self):
        SMOOTH_FACTOR = 0.3
        PRECISION = 0.45
        BREITE = 320
        LAENGE = 240
        classenames = np.array(['crooked', 'drinking', 'noperson', 'phone', 'straight'])
        
        # Should be used with a NN that outputs this classarray
        if True: # Seperation
                PRECISION = 0.4
                classenames = np.array(['crooked', 'crooked', 'drinking', 'noperson', 'phone', 'phone', 'straight'])

        fonClass = fontSummary = fontFPS = screen = surface = 0
        LOGGING = True
        
        
        # Initialize the preview window
        if self.video:
                pygame.init()
                pygame.display.init()
                pygame.font.init()
                fontClass = pygame.font.Font('./Roboto/Roboto-Bold.ttf', 12)
                fontSummary = pygame.font.Font('./Roboto/Roboto-Bold.ttf', 12)
                fontFPS = pygame.font.Font('./Roboto/Roboto-Bold.ttf', 12)
                pygame.display.set_caption('Loading')
                screen = pygame.display.set_mode((BREITE, LAENGE))
        
        # Load the TFLite model and allocate tensors.
        self.model_file, *device = self.model_file.split('@')
        interpreter= tflite.Interpreter(model_path=self.model_file, 
                experimental_delegates=[
                        tflite.load_delegate('libedgetpu.so.1', {'device': device[0]} if device else {})])                               
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Prepare smoothed array to smooth the prediction
        input_shape = input_details[0]['shape']
        smoothed = np.ones(output_details[0]['shape'][1])
        smoothed /= len(smoothed)
        
        
        lastPrediction = -1
        
        if not self.video:
                stderr.write('                    ' + str(classenames) + '\n')
        while True: #counter < 1000:
                #counter += 1
	                
                # capture an image with the camera    
                raw_frame = self.camera.next_frame()
                
                # preprocess values to be in the range 0-1
                x = np.array(raw_frame) / 255 
                
                # Resize to shape of (1, 128, 128, 3) from (128, 128, 3)
                input_data = np.array([x], dtype=np.float32) # # np.array([x])[0]

                
                interpreter.set_tensor(input_details[0]['index'], input_data)
                
                # Measure time for inference time and fps of inferencing the updated frame
                # Therefore measure the timestamp now
                inference_time_start = time.time()
                
                # Inference the NN on the picture - aka predict
                interpreter.invoke()
                
                #Get the timestamp after the inferencing to calculate the ms and fps
                inference_time_diff = time.time() - inference_time_start
                inference_time_diff_ms = round(inference_time_diff * 1000, 2)
                inference_time_diff_fps = int(1/inference_time_diff)

                # The function `get_tensor()` returns a copy of the tensor data.
                # Use `tensor()` in order to get a pointer to the tensor.
                output_data = interpreter.get_tensor(output_details[0]['index'])

                # Smooth the outputs - this adds latency but reduces oscillations between predictions
                smoothed = smoothed * SMOOTH_FACTOR + output_data[0] * (1.0 - SMOOTH_FACTOR)
                
                # The selected class is the one with highest probability
                selected = np.argmax(smoothed) 
                
                # Only give an prediction if the prediction has archieved a certain amount of propability precision
                if np.amax(smoothed) > PRECISION:
                        classname = classenames[selected]
                else:
                # Else return "No_CONFIDENCE" as classname
                        classname = "NO_CONFIDENCE"
    	
    	        # Send based on the classname an event containing the classname
                if self.sendEvents and not(classname == lastPrediction) and not(classname == "NO_CONFIDENCE"):
                        #print("Class Send: %s" % classname)
                        lastPrediction = classname
                        self.convertToEvent(classname)
                        if LOGGING:
                                self.log_file.write(str(time.time()) + ", " + classname + "\n")
                
                # String to represent the probability of each class
                summary = '[%s]' % (' '.join('%02.0f%%' % (99 * p) for p in smoothed))

                # Show the image in a preview window so you can tell if you are in frame
                # Additionally also show the classname and probability for each class
                if self.video:
                        classnameFont = fontClass.render(classname, True, (255,255,255))
                        summaryFont = fontSummary.render(summary, True, (255,255,255))

                        FPSFont = fontFPS.render(str(inference_time_diff_fps), True, pygame.Color("coral"))

                        surface = pygame.surfarray.make_surface(raw_frame)
                        surface = pygame.transform.rotate(surface, 270)
                        screen.blit(pygame.transform.smoothscale(surface, (BREITE, LAENGE)), (0, 0))
                        screen.blit(classnameFont, (BREITE * 0.45, LAENGE * 0.88))
                        screen.blit(summaryFont, (BREITE * 0.25, LAENGE * 0.93))
                        screen.blit(FPSFont, (BREITE * 0.1, LAENGE * 0.1))
                        pygame.display.flip()
                        
                        for evt in pygame.event.get():
                                if evt.type == pygame.QUIT:
                                        pygame.quit()
                                break
                else:
                        stderr.write(classname + ' in ' + str(inference_time_diff_ms) + 'ms, ' + str(inference_time_diff_fps) + 'fps | ' + summary +  '         \r')
            	


            
