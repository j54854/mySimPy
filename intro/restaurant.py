# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from operator import attrgetter

MeanArrival = 5
MeanDeparture = 20
StdvDeparture = 10
Horizon = 8 *60

class State:
    def __init__(self):
        self.now = 0
        self.nCustomers = 0

    def __repr__(self):
        return repr((self.now, self.nCustomers))

    def arrival(self, now, cal):
        self.now = now
        self.nCustomers = self.nCustomers +1
        cal.appendNext(now, "arrival")
        cal.appendNext(now, "departure")

    def departure(self, now):
        self.time = now
        self.nCustomers = self.nCustomers -1


class StateLog:
    def __init__(self):
        self.time = [0]
        self.nCustomers = [0]

    def extend(self, s):
        self.time.append(s.now)
        self.nCustomers.append(s.nCustomers)


class Event:
    def __init__(self, time, eId):
        self.time = time
        self.eId = eId
#        self.par = []

    def __repr__(self):
        return repr((self.time, self.eId))


class Calendar:
    def __init__(self):
        self.future = [
            Event(Horizon, "finished"), 
            Event(np.random.exponential(MeanArrival ,1), "arrival")]
        self.past = []

    def timeSort(self):
        self.future.sort(key = attrgetter("time"), reverse = True)

    def appendNext(self, now, eId):
        if eId == "arrival":
            self.future.append(Event(now +np.random.exponential(MeanArrival, 1), "arrival"))
        elif eId == "departure":
            timeLength = np.random.normal(MeanDeparture, StdvDeparture, 1)
            while timeLength <= 0:
                timeLength = np.random.normal(MeanDeparture, StdvDeparture, 1)
            self.future.append(Event(now +timeLength, "departure"))
        self.timeSort()

    def fireNext(self):
        nextEvent = self.future.pop()
        self.past.append(nextEvent)
        return nextEvent


def main():
    myState = State()
    myCal = Calendar()
    myLog = StateLog()

    while True:
        myEvent = myCal.fireNext()

        print(myEvent)
        print(myState)

        if myEvent.eId == "finished":
            break
        elif myEvent.eId == "arrival":
            myState.arrival(myEvent.time, myCal)
        elif myEvent.eId == "departure":
            myState.departure(myEvent.time)

        myLog.extend(myState)

    plt.plot(myLog.time, myLog.nCustomers, drawstyle = "steps-post")
    plt.xlabel("time (minute)")
    plt.ylabel("number of customers")
    plt.show()

    return myCal, myLog

if __name__ == "__main__":
    main()    
