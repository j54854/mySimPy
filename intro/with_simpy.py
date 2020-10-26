import random
import simpy


class Model():
    def __init__(self):
        self.count = 0  # an example state variable (the number of events triggered)

    def print_state(self):
        print('{} th event occurs at {}'.format(self.count, round(self.now)))



def main():
    env = simpy.Environment()
    env.model = Model(env, 10)
    env.process(manager(env))
    env.process(customer(env))
    env.run(until=200)

if __name__ == "__main__":
    main()
