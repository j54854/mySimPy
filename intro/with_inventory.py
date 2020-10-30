import matplotlib.pyplot as plt
import random
import simpy

class Model:
    def __init__(self, env, op, oq, lt, init):
        self.env = env
        self.op = op  # ordering point
        self.oq = oq  # order quantity
        self.lt = lt  # reprenishment lead time
        self.at_hand = init  # how many items you have at hand
        self.loss = 0  # opportunity loss
        self.orders = []  # list of back orders

    @property
    def total(self):
        return sum(self.orders) +self.at_hand

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
        print('[{}] current level: {}, back order: {}, lost sales: {} '.format(round(self.env.now), self.at_hand, self.orders, self.loss))
        self.env.log.extend()

    def customer(self):
        while True:
            yield self.env.timeout(random.expovariate(1))
            self.sell_or_apologize()
            self.env.activateManager.succeed()  # signal for activating manager

    def manager(self):
        self.env.activateManager = self.env.event()  # create the first signal
        while True:
            yield self.env.activateManager
            ordered = self.stocktake()
            if ordered:
                self.env.process(self.deliverer())  # activate deliverer
            self.env.activateManager = self.env.event()  # create the next signal
            self.print_state()

    def deliverer(self):
        yield self.env.timeout(self.lt)
        self.fill_up()
        self.print_state()

class Log:
    def __init__(self, env):
        self.env = env
        self.time = []
        self.at_hand = []
        self.loss = []
        self.total = []
        self.extend()

    def extend(self):
        self.time.append(self.env.now)
        self.at_hand.append(self.env.model.at_hand)
        self.loss.append(self.env.model.loss)
        self.total.append(self.env.model.total)

    def plot_log(self):
        plt.plot(self.time, self.at_hand, drawstyle = "steps-post")
        plt.xlabel("time (minute)")
        plt.ylabel("number of items")
        plt.show()

def main():
    env = simpy.Environment()
    env.model = Model(env, 10, 20, 10, 20)  # op, oq, lt, init
    env.log = Log(env)
    env.process(env.model.manager())
    env.process(env.model.customer())
    env.run(until=200)
    env.log.plot_log()

if __name__ == "__main__":
    main()
