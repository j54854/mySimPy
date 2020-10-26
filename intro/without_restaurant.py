import matplotlib.pyplot as plt
import random

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
        self.at_hand = []
        self.loss = []
        self.total = []

    def extend(self, model):
        self.time.append(model.now)
        self.at_hand.append(model.at_hand)
        self.loss.append(model.loss)
        self.total.append(model.total)

class Skelton:
    def __init__(self, horizon):
        self.now = 0  # simulation time
        self.cal = Calendar(horizon)  # event calendar
        self.add_some_event()  # an initial event is added
        self.count = 0  # an example state variable (the number of events triggered)

    def add_event(self, dt, kind):
        e = Event(self.now +dt, kind)
        self.cal.append(e)

    def add_some_event(self):
        self.add_event(random.expovariate(1), 'some_event')

    def print_state(self):
        print('{} th event occurs at {}'.format(self.count, round(self.now)))

    def run(self):
        while True:
            self.print_state()
            e = self.cal.trigger()
            print(e)
            self.now = e.time  # advance the simulation time
            self.count += 1  # increment the event counter
            if e.kind == 'end':  # time is up
                break
            else:
                self.add_some_event()  # next event is added

class Model(Skelton):
    def __init__(self, horizon, op, oq, lt, init):
        self.now = 0  # simulation time
        self.cal = Calendar(horizon)  # event calendar
        self.add_arrival()  # an arrival event is added
        self.op = op  # ordering point
        self.oq = oq  # order quantity
        self.lt = lt  # reprenishment lead time
        self.at_hand = init  # how many items you have at hand
        self.loss = 0  # opportunity loss
        self.orders = []  # list of back orders

    @property
    def total(self):  # total inventory level including back orders
        return sum(self.orders) +self.at_hand

    def add_arrival(self):  # arrival of a customer
        self.add_event(random.expovariate(1), 'arrival')

    def add_fill_up(self):  # replenishment of ordered items
        self.add_event(self.lt, 'fill_up')

    def sell_or_apologize(self):
        if self.at_hand > 0:
            self.at_hand -= 1  # an item is sold
        else:
            self.loss += 1  # sorry we are out of stock

    def fill_up(self):  # receive the first order in the list
        if len(self.orders) > 0:
            self.at_hand += self.orders.pop(0)

    def stocktake(self):
        if self.total <= self.op:
            self.orders.append(self.oq)
            return True  # ordered
        return False  # not ordered

    def print_state(self):
        print('[{}] current level: {}, back order: {}, lost sales: {} '.format(round(self.now), self.at_hand, self.orders, self.loss))

    def run(self):
        while True:
            self.print_state()
            e = self.cal.trigger()
            print(e)
            self.now = e.time  # advance the simulation time
            if e.kind == 'end':  # time is up
                break
            elif e.kind == 'fill_up':
                self.fill_up()
            elif e.kind == 'arrival':
                self.sell_or_apologize()
                self.add_arrival()
                ordered = self.stocktake()
                if ordered:
                    self.add_fill_up()

class Model4Plot(Model):
    def __init__(self, horizon, op, oq, lt, init):
        super().__init__(horizon, op, oq, lt, init)
        self.log = Log()  # <-- added
        self.log.extend(self)  # <-- added

    def run(self):
        while True:
            self.print_state()
            self.log.extend(self)  # <-- added
            e = self.cal.trigger()
            print(e)
            self.now = e.time
            if e.kind == 'end':
                break
            elif e.kind == 'fill_up':
                self.fill_up()
            elif e.kind == 'arrival':
                self.sell_or_apologize()
                self.add_arrival()
                ordered = self.stocktake()
                if ordered:
                    self.add_fill_up()

def main():
    model = Model4Plot(200, 10, 20, 10, 20)  # horizon, op, oq, lt, init
    model.run()

    plt.plot(model.log.time, model.log.at_hand, drawstyle = "steps-post")
    plt.xlabel("time (minute)")
    plt.ylabel("number of items")
    plt.show()

if __name__ == '__main__':
    main()
