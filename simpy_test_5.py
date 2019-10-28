import random
import simpy

class CustomStore(simpy.Store):
    def __init__(self, env, capacity=float('inf')):
        super(CustomStore, self).__init__(env, capacity)

    def _do_get(self, event):
        if self.items:
            event.succeed(self.items.pop(len(self.items) -1))

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
    env.store = CustomStore(env)
    env.process(maker(env))
    env.process(buyer(env))
    env.run()

if __name__ == "__main__":
    main()
