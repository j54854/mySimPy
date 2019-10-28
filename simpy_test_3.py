import random
import simpy

class CustomContainer(simpy.Container):
    def __init__(self, env, capacity=float('inf'), init=0):
        self.env = env
        super(CustomContainer, self).__init__(env, capacity, init)

    def _trigger_get(self, put_event):
        if len(self.get_queue) > 0:
            e = self.get_queue[len(self.get_queue) -1]
            if not hasattr(e, 'now'):
                e.now = self.env.now
        super(CustomContainer, self)._trigger_get(put_event)

    def _do_get(self, event):
        if self._level >= event.amount:
            print('I waited for {} time units.'.format(round(self.env.now -event.now)))
        super(CustomContainer, self)._do_get(event)

    def report(self):
        print('[{}] current level: {}, orderd: {}, queue length: {} '.format(round(self.env.now), self.level, self.ordered, len(self.get_queue)))


def manager(env):
    env.model.ordered = False  # no back order to receive
    env.stocktake = env.event()  # create the first signal (event)
    while True:
        yield env.stocktake
        env.model.report()
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

def main():
    env = simpy.Environment()
    env.model = CustomContainer(env, init=10)
    env.process(manager(env))
    env.process(customer(env))
    env.run(until=200)

if __name__ == "__main__":
    main()
