import random
import simpy


class Skelton:
    def __init__(self, env):
        self.env = env  # pointer to the SimPy environment
        self.count = 0  # an example state variable

    def update(self, e):
        self.count += 1

    def print_state(self):
        print('{} th event occurs at {}'.format(self.count, round(self.env.now)))

    def run(self):
        while True:
            e = simpy.Timeout(self.env, random.expovariate(1))
            e.callbacks.append(self.update)
            if self.env.now > 200:
                break
            else:
                self.print_state()
                self.env.step()


class Skelton2:
    def __init__(self, env):
        self.env = env  # pointer to the SimPy environment
        self.count = 0  # an example state variable

    def print_state(self):
        print('{} th event occurs at {}'.format(self.count, round(self.env.now)))

    def process_method(self):  # an example process method
        while True:
            self.print_state()
            yield simpy.Timeout(self.env, random.expovariate(1))
            self.count += 1  # <- Skelton's update()

def process_func(env):  # an example process function
    while True:
        env.model.print_state()
        yield simpy.Timeout(env, random.expovariate(1))
        env.model.count += 1  # <- Skelton's update()


class Skelton3(Skelton2):
    def __init__(self, env):
        super().__init__(env)

    def main_process(self):
        while True:
            self.print_state()
            yield self.env.timeout(random.expovariate(1))  # shortcut for simpy.Timeout()
            self.count += 1
            if self.count %3 == 0:
                self.env.signal4A.succeed()  # signal for resuming sub process A

    def sub_process_A(self):
        self.env.signal4A = self.env.event()  # create the first signal
        while True:
            yield self.env.signal4A
            print('> sub process A is resumed at {}'.format(round(self.env.now)))
            self.env.signal4A = self.env.event()  # create the next signal
            if self.count %5 == 0:
                self.env.process(self.sub_process_B())  # register sub process B

    def sub_process_B(self):
        print('>> sub process B is started at {}'.format(round(self.env.now)))
        yield self.env.timeout(10) # shortcut for simpy.Timeout()
        print('>> sub process B is finished at {}'.format(round(self.env.now)))


def main():
    env = simpy.Environment()
    env.model = Skelton3(env)
    env.process(env.model.main_process())
    env.process(env.model.sub_process_A())
    env.run(until=200)

if __name__ == "__main__":
    main()
