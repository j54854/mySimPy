import matplotlib.pyplot as plt
import random
import simpy

class Model(simpy.Container):
    def __init__(self, env, op, oq, lt, init):
        super().__init__(env, capacity=cap, init=init)
        self.env = env
        self.op = op  # ordering point
        self.oq = oq  # order quantity
        self.lt = lt  # replenishment lead time
        self.orders = []  # list of back orders

    @property
    def total(self):
        return sum(self.orders) +self.level

    def print_state(self):
        print('[{}] current level: {}, back order: {}, queue length: {} '.format(round(self.env.now), self.level, self.orders, len(self.get_queue)))
        self.env.log.extend()

    def seller(self):
        while True:
            yield self.env.timeout(random.expovariate(1))
            self.env.process(self.buyer())  # activate a buyer
            self.print_state()  # state when a new customer arrives

    def buyer(self):
        yield self.get(1)
        if not self.env.stocktake.triggered:
            self.env.stocktake.succeed()  # activate the stocktaker

    def stocktaker(self):
        self.env.stocktake = self.env.event()  # create the first signal
        while True:
            yield self.env.stocktake
            if self.total <= self.op:
                self.orders.append(self.oq)
                self.env.process(self.deliverer())  # activate the deliverer
            self.env.stocktake = self.env.event()  # create the next signal

    def deliverer(self):
        self.print_state()  # state just after placing an order
        yield self.env.timeout(self.lt)
        oq = self.orders.pop(0)
        self.print_state()  # state just before replenishment
        yield self.put(oq)
        self.print_state()  # state just after replenishment

class Log:
    def __init__(self, env):
        self.env = env
        self.time = []
        self.level = []
        self.queue_length = []
        self.total = []
        self.extend()

    def extend(self):
        self.time.append(self.env.now)
        self.level.append(self.env.model.level)
        self.queue_length.append(len(self.env.model.get_queue))
        self.total.append(self.env.model.total)

    def plot_log(self):
        plt.plot(self.time, self.level, drawstyle = "steps-post")
        plt.xlabel("time (minute)")
        plt.ylabel("number of items")
        plt.show()

def main():
    env = simpy.Environment()
    env.model = Model(env, 10, 20, 10, 20)  # op, oq, lt, init
    env.log = Log(env)
    env.process(env.model.seller())
    env.process(env.model.stocktaker())
    env.run(until=200)
    env.log.plot_log()

if __name__ == "__main__":
    main()
