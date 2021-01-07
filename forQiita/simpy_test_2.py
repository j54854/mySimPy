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
    yield env.model.put(20)  # back order is received
    env.model.ordered = False  # no back order to receive

def customer(env):
    while True:
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        how_many = random.randint(1, 3)
        yield env.model.get(how_many)
        env.stocktake.succeed()  # signal for stocktaking (event)

def report(env):
    print('[{}] current level: {}, ordered: {}, queue length: {} '.format(round(env.now), env.model.level, env.model.ordered, len(env.model.get_queue)))

def main():
    env = simpy.Environment()
    env.model = simpy.Container(env, init=10)  # model is marely a Container
    env.process(manager(env))
    env.process(customer(env))
    env.run(until=200)

if __name__ == "__main__":
    main()
