import random
import simpy
from p5 import *

def manager(env):
    env.model.ordered = False  # no back order to receive
    env.stocktake = env.event()  # create the first signal (event)
    while True:
        yield env.stocktake
        report(env)
        if not env.model.ordered and env.model.level <= 10:
        # only when no back order to receive
        # reorder point = 10
            env.process(deliverer(env))  # activate deliverer
            env.model.ordered = True  # back order will be received
        env.stocktake = env.event()  # create the next signal (event)

def deliverer(env):
    yield env.timeout(5)  # delivery lead time = 5
    env.model.put(20)  # back order is recieved
    env.model.ordered = False  # no back order to receive

def customer(env):
    while True:
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        how_many = random.randint(1, 3)
        env.model.get(how_many)
        env.stocktake.succeed()  # signal for stocktaking (event)

def report(env):
    print('[{}] current level: {}, orderd: {}, queue length: {} '.format(round(env.now), env.model.level, env.model.ordered, len(env.model.get_queue)))

def simpy_setup():  # setup of simpy environment
    env = simpy.Environment()
    env.model = simpy.Container(env, init=10)  # model is marely a Container
    env.process(manager(env))
    env.process(customer(env))
#    env.run(until=200)
    return env

# ---------- code for visualization ----------
def setup():  # setup of p5py sketch
    size(600, 600)

def draw():  # drawing loop of visualization by p5py
    background(255)
    if frame_count <= 200:
        simpy_env.run(until=frame_count)  # keep pace with draw()
        level = simpy_env.model.level
        queue = len(simpy_env.model.get_queue)
        ordered = simpy_env.model.ordered
    else:
        exit()

    translate(250, 350)
    line((-200, 0), (300, 0))
    if queue > 0:
        fill(127, 0, 0)
        rect((0,0), 100, 10 *queue)
    if level > 0:
        fill(127)
        rect((0,0), 100, -10 *level)
    translate(0, -10 *level)
    if ordered:
        fill(255)
        rect((0,0), 100, -10 *20)
# ---------- ---------- ---------- ----------

if __name__ == "__main__":
    simpy_env = simpy_setup()
    run(frame_rate=10)  # you can control the speed here
