import random
import simpy

class Model():
    def __init__(self, env, init):
        self.env = env
        self.at_hand = init  # how many items you have at hand
        self.losses = 0  # opportunity losses
        self.orders = []  # list of back orders

    @property
    def total(self):
        return sum(self.orders) +self.at_hand

    def send_out(self):
        if self.at_hand > 0:
            self.at_hand -= 1
        else:
            self.losses += 1

    def receive(self):
        if len(self.orders) > 0:
            self.at_hand += self.orders.pop(0)

    def order(self, num):  # num = order quantity
        self.orders.append(num)
        self.env.process(deliverer(self.env))  # activate deliverer

    def report(self):
        print('[{}] current level: {}, back order: {}, lost sales: {} '.format(round(self.env.now), self.at_hand, self.orders, self.losses))

def customer(env):
    while True:
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        env.model.send_out()
        env.stocktake.succeed()  # signal for stocktaking (event)

def manager(env):
    env.stocktake = env.event()  # create the first signal (event)
    while True:
        yield env.stocktake
        env.model.report()
        if env.model.total <= 10:  # reorder point = 10
            env.model.order(20)  # order quantity = 20
        env.stocktake = env.event()  # create the next signal (event)

def deliverer(env):
    yield env.timeout(10)  # delivery lead time = 10
    env.model.receive()

def main():
    env = simpy.Environment()
    env.model = Model(env, 10)
    env.process(manager(env))
    env.process(customer(env))
    env.run(until=200)

if __name__ == "__main__":
    main()
