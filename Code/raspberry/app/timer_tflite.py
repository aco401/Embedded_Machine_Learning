import time
import threading
from defines_tflite import StateEvents, Topics, ActionsEvents
from pubsub import pub 

class Timer(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.registerTopic(Topics.TOPIC_TIMER.value)
        self.stop_counter = 0
        self.dr_counter = 0
        self.dr_temp = 0
        self.wd_counter = 0
        self.wd_temp = 0
        self.cr_counter = 0
        self.ph_counter = 0
        
    def run(self):
        while(1):
                time.sleep(2)
                curr_time = self.getTime()
                #print("time: " + str(self.getTime()) + ", cr_counter: " + str(int(self.cr_counter)) + ", dr_counter: " + str(int(self.dr_counter)) + ", wd_counter: " + str(int(self.wd_counter)))

                if (self.dr_counter != 0) and (self.dr_counter < curr_time):
                        #print("DR_TIMER_OVER")
                        self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.DR_TIMER_OVER.value)
                        self.dr_counter = 0
                        
                if (self.cr_counter != 0) and (self.cr_counter < curr_time):
                        #print("CR_TIMER_OVER")
                        self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.CR_TIMER_OVER.value)
                        self.cr_counter = 0

                if (self.wd_counter != 0) and (self.wd_counter < curr_time):
                        #print("WD_TIMER_OVER")
                        self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.WD_TIMER_OVER.value)
                        self.wd_counter = 0

                if (self.ph_counter != 0) and (self.ph_counter < curr_time):
                        #print("PH_TIMER_OVER")
                        self.throwEvent(Topics.TOPIC_STATEMACHINE.value, StateEvents.PH_TIMER_OVER.value)
                        self.ph_counter = 0
                
    def registerTopic(self, event):
        pub.subscribe(self.notifyEvent, event)
        
    def throwEvent(self, topic, event):
        pub.sendMessage(topic, arg1=event)
                
    def isCounterZero(self):
        return (self.stop_counter == 0) and (self.dr_counter == 0)
        
        
    # PubSub
    def notifyEvent(self, arg1, arg2):
        #print("Timer notifyEvent: arg1:" + str(arg1) + ", arg2: " + str(arg2))
        if (arg1 == StateEvents.DR_TIMER_START.value):
                self.dr_counter = self.getTime() + arg2

        elif arg1 == StateEvents.DR_TIMER_STOP.value:
                self.dr_counter = 0

        elif ((arg1 == StateEvents.DR_TIMER_PAUSE.value) and (self.dr_counter != 0) and (self.dr_temp == 0)):
                self.dr_temp = self.dr_counter - self.getTime()
                self.dr_counter = 0

        elif ((arg1 == StateEvents.DR_TIMER_RESUME.value) and (self.dr_counter == 0) and (self.dr_temp != 0)):
                self.dr_counter = self.getTime() + self.dr_temp
                self.dr_temp = 0

        elif (arg1 == StateEvents.CR_TIMER_START.value):
                self.cr_counter = self.getTime() + arg2
                #print("Timer: CR_TIMER_START")

        elif arg1 == StateEvents.CR_TIMER_STOP.value:
                self.cr_counter = 0
                #print("Timer: CR_TIMER_STOP")

        elif (arg1 == StateEvents.WD_TIMER_START.value):
                self.wd_counter = self.getTime() + arg2
                #print("Timer: WD_TIMER_START")

        elif arg1 == StateEvents.WD_TIMER_STOP.value:
                self.wd_counter = 0
                #print("Timer: WD_TIMER_STOP")

        elif ((arg1 == StateEvents.WD_TIMER_PAUSE.value) and (self.wd_counter != 0) and (self.wd_temp == 0)):
                self.wd_temp = self.wd_counter - self.getTime()
                self.wd_counter = 0
                #print("Timer: WD_TIMER_PAUSE")

        elif ((arg1 == StateEvents.WD_TIMER_RESUME.value) and (self.wd_counter == 0) and (self.wd_temp != 0)):
                self.wd_counter = self.getTime() + self.wd_temp
                self.wd_temp = 0
                #print("Timer: WD_TIMER_RESUME")

        elif (arg1 == StateEvents.PH_TIMER_START.value):
                self.ph_counter = self.getTime() + arg2
                #print("Timer: PH_TIMER_START")

        elif arg1 == StateEvents.PH_TIMER_STOP.value:
                self.ph_counter = 0
                #print("Timer: PH_TIMER_STOP")

                
                
    def getTime(self):
        return time.time()
