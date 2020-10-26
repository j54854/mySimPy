import matplotlib.pyplot as plt
import random, math

class Event:
    def __init__(self, time, kind):
        self.time = time  # when this event occurs
        self.kind = kind  # the type of this event

    def __str__(self):
        return self.kind

class Calendar:
    def __init__(self, horizon):
        self.queue = [Event(horizon, 'end')]  # list of events

    def append(self, e):  # add a new event to the list
        self.queue.append(e)
        self.queue.sort(key=lambda x: x.time)  # sort events chronologically

    def trigger(self):  # trigger the first event in the list
        e = self.queue.pop(0)
        return e

class Log:
    def __init__(self):
        self.time = []
        self.in_queue = []
        self.in_seats = []
        self.loss = []

    def extend(self, model):
        self.time.append(model.now)
        self.in_queue.append(model.in_queue)
        self.in_seats.append(model.in_seats)
        self.loss.append(model.loss)

class Model:
    def __init__(self, horizon, cap, ub, mt, vt):
        self.now = 0  # simulation time
        self.cal = Calendar(horizon)  # event calendar
        self.add_arrival()  # an arrival event is added
        self.cap = cap  # number of seats
        self.ub = ub  # maximum queue length
        self.mt = mt  # mean of eating time
        self.vt = vt  # variance of eating time
        self.in_queue = 0  # number of customers waiting
        self.in_seats = 0  # number of customers eating
        self.loss = 0  # opportunity loss
        self.log = Log()
        self.log.extend(self)

    def add_event(self, dt, kind):
        e = Event(self.now +dt, kind)
        self.cal.append(e)

    def add_arrival(self):  # a customer's arrival 
        self.add_event(random.expovariate(1), 'arrival')

    def add_departure(self):  # a customer's departure
        eating_time = 0
        while eating_time <= 0:  # eating time must be > 0
            eating_time = random.normalvariate(self.mt, math.sqrt(self.vt))
        self.add_event(eating_time, 'departure')

    def wait_or_leave(self):
        if self.in_queue < self.ub:
            self.in_queue += 1  # join the queue
        else:
            self.loss += 1  # give up and go home

    def say_goodbye(self):  # finish eating and leave
        self.in_seats -= 1

    def is_seatable(self):  # at least an empty seat and a waiting customer
        if self.in_seats < self.cap and self.in_queue > 0:
            return True
        return False

    def seat_customer(self):  # move a customer from queue to a seat
        self.in_queue -= 1
        self.in_seats += 1

    def print_state(self):
        print('[{}] in queue: {}, in seats: {}, lost sales: {} '.format(round(self.now), self.in_queue, self.in_seats, self.loss))

    def run(self):
        while True:
            self.print_state()
            self.log.extend(self)
            e = self.cal.trigger()
            print(e)
            self.now = e.time  # advance the simulation time
            if e.kind == 'end':  # time is up
                break
            elif e.kind == 'departure':
                self.say_goodbye()
            elif e.kind == 'arrival':
                self.wait_or_leave()
                self.add_arrival()
            if self.is_seatable():
                self.seat_customer()
                self.add_departure()

def main():
    model = Model(200, 30, 10, 25, 25)  # horizon, cap, ub, mt, vt
    model.run()

    plt.plot(model.log.time, model.log.in_queue, drawstyle = "steps-post")
    plt.xlabel("time (minute)")
    plt.ylabel("queue length")
    plt.show()

if __name__ == '__main__':
    main()
