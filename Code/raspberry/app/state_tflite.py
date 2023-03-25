from statemachine import StateMachine, State
from statemachine.exceptions import TransitionNotAllowed
from defines_tflite import StateEvents, Topics, ActionsEvents
from pubsub import pub
from collections import deque
import threading


class ProcrastinationMachine(StateMachine, threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        StateMachine.__init__(self)
        self.q = deque()
        pub.subscribe(self.notifyEvent, Topics.TOPIC_STATEMACHINE.value)
        self.lock = threading.Lock()
        self.drink_timer = int(20*60) # 20 min # drinking
        self.wd_timer = int(45*60) # 45 min # window
        self.ph_timer = 2 # phone
        self.cr_timer = 2 # crooked

    #def init(self):

    def run(self):
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_START.value, self.drink_timer)
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_START.value, self.wd_timer)
        while(1):
            if not(len(self.q) == 0):
            #print("AudioActions started")
                self.checkEvent(self.q.popleft())
        
    def throwEvent(self, topic, event):
        pub.sendMessage(topic, arg1=event)
        
    def throwEventTimer(self, topic, event, data):
        pub.sendMessage(topic, arg1=event, arg2=data)
        
            
    #State Definition
    work = State('Work', initial=True)
    drinkAction = State('DrinkAction')
    crookedBack = State('CrookedBack')
    wdCommand = State('WDCommand')
    openWindow = State('OpenWindow')

    #Transitions
    noperson = wdCommand.to(openWindow)
    drinking = work.to(work) | drinkAction.to(work) | openWindow.to(work) | crookedBack.to(crookedBack)
    crooked = work.to(crookedBack) | openWindow.to(work)
    straight = crookedBack.to(work) | openWindow.to(work) | work.to(work)
    phone = work.to(work) | openWindow.to(work)
    cr_timer_over = crookedBack.to(crookedBack)
    dr_timer_over = work.to(drinkAction) | crookedBack.to(drinkAction) | drinkAction.to(drinkAction)
    wd_timer_over = work.to(wdCommand) | wdCommand.to(wdCommand) | crookedBack.to(wdCommand)
    ph_timer_over = work.to(work)


    def notifyEvent(self, arg1):
        self.q.append(arg1)
        
    def checkEvent(self, arg1):
        #print("Received:" + arg1)
        self.lock.acquire()
        #print("state received: " + str(arg1))
        try:
            if arg1 == StateEvents.NOPERSON.value:
                self.noperson()
            elif arg1 == StateEvents.CROOKED.value:
                self.crooked()
            elif arg1 == StateEvents.DRINKING.value:
                self.drinking()
            elif arg1 == StateEvents.STRAIGHT.value:
                self.straight()
            elif arg1 == StateEvents.PHONE.value:
                self.phone()
            elif arg1 == StateEvents.DR_TIMER_OVER.value:
                self.dr_timer_over()
            elif arg1 == StateEvents.CR_TIMER_OVER.value:
                self.cr_timer_over()
            elif arg1 == StateEvents.WD_TIMER_OVER.value:
                self.wd_timer_over()
            elif arg1 == StateEvents.PH_TIMER_OVER.value:
                self.ph_timer_over()
            #print("current state: " + str(self.current_state))
            self.lock.release()
        except TransitionNotAllowed:
            #print("Transition not possible: ", arg1)
            self.lock.release()
                
            
    #Transition Callbacks
    def on_drinking(self):
        if self.is_drinkAction:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_START.value, self.drink_timer)
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_RESUME.value, 0)
        elif self.is_work or self.is_crookedBack:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_START.value, self.drink_timer)

        if self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)

    def on_dr_timer_over(self):
        #print("state: dr_timer_over func, state: " + str(self.current_state))

        # Because on_dr_timer_over is executed before even the state transition happened
        if self.is_drinkAction or self.is_work or self.is_crookedBack:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_START.value, 5)
            #print("state: send dr_timer_start(5)")
        
        if self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)

        if self.is_crookedBack or self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_PAUSE.value, 0)
    
    def on_noperson(self):
        if self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)
        
    def on_phone(self):
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_START.value, self.ph_timer)

    def on_ph_timer_over(self):
        self.throwEvent(Topics.TOPIC_ACTIONS.value, ActionsEvents.AUDIO_PHONE.value)
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_START.value, self.ph_timer)
        

    def on_crooked(self):
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.CR_TIMER_START.value, self.cr_timer)
        #print("state: on_crooked: CR_TIMER_START send")

        if self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)

    def on_cr_timer_over(self):
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.CR_TIMER_START.value, self.cr_timer)
        self.throwEvent(Topics.TOPIC_ACTIONS.value, ActionsEvents.AUDIO_CROOKED.value)
        #print("state: on_cr_timer_over: CR_TIMER_START send")

    def on_straight(self):
        if self.is_crookedBack:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.CR_TIMER_STOP.value, 0)
            #print("is____ worked")
        
        if self.is_work:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)

    def on_wd_timer_over(self):
        if self.is_work or self.is_crookedBack:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_PAUSE.value, 0)
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_START.value, 5)
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.PH_TIMER_STOP.value, 0)
        elif self.is_wdCommand:
            self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_START.value, 5)

        
        
            
            

    #Entry/Exit
                    
    def on_enter_crookedBack(self):
        #self.throwEvent(Topics.TOPIC_ACTIONS.value, ActionsEvents.AUDIO_CROOKED.value)
        print("state entered crookedBack")
            
    def on_enter_drinkAction(self):
        self.throwEvent(Topics.TOPIC_ACTIONS.value, ActionsEvents.AUDIO_DRINK.value)
        print("state entered drinkAction")

    def on_enter_wdCommand(self):
        self.throwEvent(Topics.TOPIC_ACTIONS.value, ActionsEvents.AUDIO_WD_OPEN.value)
            
    def on_exit_openWindow(self):
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.WD_TIMER_START.value, self.wd_timer)
        self.throwEventTimer(Topics.TOPIC_TIMER.value, StateEvents.DR_TIMER_RESUME.value, 0)
