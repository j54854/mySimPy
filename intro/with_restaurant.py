import matplotlib.pyplot as plt
import random, math
import simpy

class Model:
    def __init__(self, env, cap, ub, mt, vt):
        self.env = env
        self.cap = cap  # number of seats
        self.ub = ub  # maximum queue length
        self.mt = mt  # mean of eating time
        self.vt = vt  # variance of eating time
        self.in_queue = 0  # number of customers waiting
        self.in_seats = 0  # number of customers eating
        self.loss = 0  # opportunity loss

    def say_goodbye(self):  # finish eating and leave
        self.in_seats -= 1

    def is_seatable(self):  # at least an empty seat and a waiting customer
        return self.in_seats < self.cap and self.in_queue > 0

    def seat_customer(self):  # move a customer from queue to a seat
        self.in_queue -= 1
        self.in_seats += 1

    def print_state(self):
        print('[{}] in queue: {}, in seats: {}, lost sales: {} '.format(round(self.env.now), self.in_queue, self.in_seats, self.loss))

    def reception(self):  # deal with arriving potential customers
        while True:
            yield self.env.timeout(random.expovariate(1))
            if self.in_queue < self.ub:
                self.in_queue += 1  # join the queue
                self.env.activateServer.succeed()  # signal for activating the server
            else:
                self.loss += 1  # give up and go home

    def server(self):  # the server of the restaurant
        while True:
            self.env.activateServer = self.env.event()  # create the signal
            yield self.env.activateServer
            if self.is_seatable():
                self.seat_customer()
                self.env.process(self.customer())  # activate a customer
            self.print_state()
            self.env.log.extend()

    def customer(self):  # a customer having lunch
        eating_time = 0
        while eating_time <= 0:  # eating time must be > 0
            eating_time = random.normalvariate(self.mt, math.sqrt(self.vt))
        yield self.env.timeout(eating_time)
        self.say_goodbye()
        self.env.activateServer.succeed()  # signal for activating the server

class Log:
    def __init__(self, env):
        self.env = env
        self.time = []
        self.in_queue = []
        self.in_seats = []
        self.loss = []
        self.extend()

    def extend(self):
        self.time.append(self.env.now)
        self.in_queue.append(self.env.model.in_queue)
        self.in_seats.append(self.env.model.in_seats)
        self.loss.append(self.env.model.loss)

    def plot_log(self):
        plt.plot(self.time, self.in_queue, drawstyle = "steps-post")
        plt.xlabel("time (minute)")
        plt.ylabel("queue length")
        plt.show()

def main():
    env = simpy.Environment()
    env.model = Model(env, 30, 10, 25, 25)  # cap, ub, mt, vt
    env.log = Log(env)
    env.process(env.model.reception())
    env.process(env.model.server())
    env.run(until=200)
    env.log.plot_log()

if __name__ == '__main__':
    main()
