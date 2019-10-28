import random
import simpy

def maker(env):
    for i in range(100):
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        yield env.store.put('product_' +str(i))  # put string "product_i" into Store

def buyer(env):
    for j in range(100):
        time_to = random.expovariate(1)
        yield env.timeout(time_to)
        item = yield env.store.get()  # get string "product_i" from Store and assign it to item
        print('buyer_{} bought {}.'.format(j, item))

def main():
    env = simpy.Environment()
    env.store = simpy.Store(env)
    env.process(maker(env))
    env.process(buyer(env))
    env.run()

if __name__ == "__main__":
    main()
