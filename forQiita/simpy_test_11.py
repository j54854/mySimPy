import random
import simpy
from p5 import *

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
        print('{}: I have {}, orderd {}, and lost {}. '.format(round(self.env.now), self.at_hand, self.orders, self.losses))

def customer(env):
    while True:
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        env.model.send_out()
        env.model.report()
        env.stocktake.succeed()  # check inventory level (event)

def manager(env):
    env.stocktake = env.event()  # create first event
    while True:
        yield env.stocktake
        if env.model.total <= 10:  # reorder point = 10
            env.model.order(20)  # order quantity = 20
            env.model.report()
        env.stocktake = env.event()  # create next event

def deliverer(env):
    yield env.timeout(10)  # delivery lead time = 10
    env.model.receive()
    env.model.report()

def simpy_setup():  # setup of simpy environment
    env = simpy.Environment()
    env.model = Model(env, 10)
    env.process(customer(env))
    env.process(manager(env))
    return env

def setup():  # setup of p5py sketch
    size(600, 600)

def draw():  # drawing loop of visualization by p5py
    background(255)
    if frame_count <= 200:
        simpy_env.run(until=frame_count)  # keep pace with draw()
        at_hand = simpy_env.model.at_hand
        losses = simpy_env.model.losses
        orders = simpy_env.model.orders
    else:
        exit()

    translate(250, 350)
    line((-200, 0), (300, 0))
    if losses > 0:
        fill(127, 0, 0)
        rect((0,0), 100, 10 *losses)
    if at_hand > 0:
        fill(127)
        rect((0,0), 100, -10 *at_hand)
    translate(0, -10 *at_hand)
    for order in orders:
        if order > 0:
            fill(255)
            rect((0,0), 100, -10 *order)
            translate(0, -10 *order)

if __name__ == "__main__":
    simpy_env = simpy_setup()
    run(frame_rate=10)  # you can control the speed here
