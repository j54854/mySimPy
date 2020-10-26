import numpy as np
import matplotlib.pyplot as plt
import random
import simpy

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

# ---------- code for visualization ----------
    env.x.append(env.now)  # time
    env.y.append(env.model.level)  # container's level
# ---------- ---------- ---------- ----------

def main():
    env = simpy.Environment()
    env.model = simpy.Container(env, init=10)  # model is marely a Container
    env.process(manager(env))
    env.process(customer(env))
#    env.run(until=200)

# ---------- code for visualization ----------
    env.x = [0]  # time
    env.y = [10]  # container's level
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.set_xlabel('time')
    ax.set_ylabel('number')
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 30)
    line, = ax.plot(env.x, env.y, label='level')
    ax.legend()
    ax.grid()
    for t in range(1, 200):
        env.run(until=t)  # stepwise execution
        line.set_data(env.x, env.y)
        plt.pause(0.1)
    plt.show()
# ---------- ---------- ---------- ----------

if __name__ == "__main__":
    main()
