import sys
import threading
from pubsub import pub
from timer_tflite import Timer
from defines_tflite import Topics, StateEvents, ActionsEvents
from audioActions_tflite import AudioActions
from state_tflite import ProcrastinationMachine
import time
from classificator_tflite import classificator

def main(argv):
    timer = Timer(11)
    timer.start()
    audio = AudioActions(2)
    audio.start()
    state = ProcrastinationMachine(10)
    state.start()
    
    if (len(argv) < 1) or (len(argv) > 3):
    	print('''Usage: app.py tflite-FILE [VIDEO]
    	VIDEO - without no video is displayed
    	Your input: app.py %s"''' % argv)
    	exit(1)
    print(argv)
    video = False
    model = argv[0]
    if 'video' in argv:
        video = True
    try:
    	clf = classificator(1, model, video, sendEvents=True, res=(128,128))
    	clf.start()
    	print("Classificator")
    except (KeyBoardInterrupt, SystemExit):
    	print('\n! Received keyboard interrupt, quitting threads.\n')#
    
    #pub.sendMessage(Topics.TOPIC_TIMER.value, arg1=StateEvents.DR_TIMER_START.value, arg2=5)
    #pub.sendMessage(Topics.TOPIC_TIMER.value, arg1=StateEvents.DR_TIMER_START.value, arg2=2)
    #pub.sendMessage(topicName=Topics.TOPIC_ACTIONS.value, arg1=ActionsEvents.AUDIO_CROOKED.value)
    #pub.sendMessage(topicName=Topics.TOPIC_ACTIONS.value, arg1=ActionsEvents.AUDIO_PHONE.value)
    #pub.sendMessage(Topics.TOPIC_ACTIONS.value, arg1=ActionsEvents.AUDIO_CROOKED.value)
    #pub.sendMessage(Topics.TOPIC_STATEMACHINE.value, arg1=StateEvents.CROOKED.value)
    
    
if __name__ == '__main__':
    main(sys.argv[1:])
