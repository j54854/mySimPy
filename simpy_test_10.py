import numpy as np
import matplotlib.pyplot as plt
import simpy
import math

STATES = 25  # state in ((,-1], [0, 1], [2, 3], ..., [46,))
ACTIONS = 10  # action in (0, 3, 6, 9, 12, 15, 18, 21, 24, 25)
ORDER_COST = 1
STOCK_COST = 0.025
PENALTY = 0.1
DISCOUNT = 0.9
LEARNING = 0.2

class CustomContainer(simpy.Container):
    def __init__(self, env, capacity=float('inf'), init=0):
        self.env = env
        self.orders = []  # list of back orders
        super(CustomContainer, self).__init__(env, capacity, init)

    @property
    def shortage(self):  # total amount requested by waiting customers
        num = 0
        for customer in self.get_queue:
            num += customer.amount
        return num

    def get_state(self):  # return encoded state number
        total = self.level +sum(self.orders) -self.shortage
        return max(0, min(math.floor(total /2) +1, STATES -1))

    def get_reward(self, action):  # negative reward or cost
        reward = self.level *STOCK_COST +self.shortage *PENALTY
        if action > 0:
            reward += ORDER_COST
        return reward

class Agent:
    def __init__(self, env):
        self.env = env
        self.epsilon = 0.1
        self.recent_rewards = [0] *100
        self.Q = np.random.rand(STATES *ACTIONS).reshape(STATES, ACTIONS) *10
        self.Q[0][0] = math.inf
        for a in range(1, ACTIONS):
            self.Q[STATES -1][a] = math.inf

    @property
    def average_reward(self):
        return sum(self.recent_rewards) /len(self.recent_rewards)

    def e_greedy(self, state):
        if state == 0:  # you should order at least some amount
            if self.epsilon <= np.random.rand():
                return self.Q[state].argmin()  # greedy
            else:
                return np.random.randint(1, ACTIONS)  # random
        elif state == STATES -1:  # you cannot order
            return 0
        elif self.epsilon <= np.random.rand():
            return self.Q[state].argmin()  # greedy
        else:
            return np.random.randint(0, ACTIONS)  # random

    def move(self):
        state_to = self.env.model.get_state()
        while True:
            state_from = state_to
            action = self.e_greedy(state_from)
            if action > 0:  # when you order
                self.env.model.orders.append(action *3)
                self.env.process(deliverer(self.env))  # activate deliverer
                if not self.env.record.triggered:
                    self.env.record.succeed()  # record log
            yield self.env.timeout(1)  # periodic inventory check
            state_to = self.env.model.get_state()
            reward = self.env.model.get_reward(action)
            self.recent_rewards.append(reward)
            self.recent_rewards.pop(0)
            self.update_Q(state_from, action, state_to, reward)

    def update_Q(self, state_from, action, state_to, reward):
        Q_to_min = self.Q[state_to].min()
        self.Q[state_from][action] += LEARNING *(reward +DISCOUNT *Q_to_min -self.Q[state_from][action])

    def update_epsilon(self):
        self.epsilon *= 0.9

def deliverer(env):
    yield env.timeout(3)  # delivery lead time = 3
    env.model.put(env.model.orders.pop(0))

def customer(env):
    while True:
        time_to = np.random.exponential(1)
        yield env.timeout(time_to)
        how_many = np.random.randint(1, 8)  # mean = 4
        env.model.get(how_many)
        if not env.record.triggered:
            env.record.succeed()  # record log

def recorder(env):  # process for recording log for visualization
    _t = []
    env.record = env.event()
    while True:
        yield env.record
        _t.append(env.now)
        env.y11.append(env.model.level)
        env.y12.append(sum(env.model.orders))
        env.y13.append(env.model.shortage)
        env.t.append(env.now)
        env.z.append(env.agent.average_reward)
        if env.now > 200:
            t_min = env.now -200
            env.y11 = [
                env.y11[i] for i in range(len(_t)) if _t[i] > t_min
                ]
            env.y12 = [
                env.y12[i] for i in range(len(_t)) if _t[i] > t_min
                ]
            env.y13 = [
                env.y13[i] for i in range(len(_t)) if _t[i] > t_min
                ]
            _t = [_t[i] for i in range(len(_t)) if _t[i] > t_min]
            env.x = [_t[i] -max(_t) +200 for i in range(len(_t))]
        else:
            env.x = _t
        env.record = env.event()

def main():
    env = simpy.Environment()
    env.model = CustomContainer(env)
    env.agent = Agent(env)
    env.process(recorder(env))
    env.process(customer(env))
    env.process(env.agent.move())
# ---------- code for visualization ----------
    env.x = []
    env.y11 = []
    env.y12 = []
    env.y13 = []
    env.t = []
    env.z = []

    fig = plt.figure(1, figsize=(12, 8))

    ax1 = fig.add_subplot(221)
    ax1.set_xlabel('time')
    ax1.set_ylabel('cost')
    ax1.set_xlim(0, 50000)
    ax1.set_ylim(0, 2)
    line1, = ax1.plot(env.t, env.z, label='average cost')
    ax1.legend()
    ax1.grid()

    ax2 = fig.add_subplot(222)
    ax2.set_xlabel('time')
    ax2.set_ylabel('number')
    ax2.set_xlim(0, 200)
    ax2.set_ylim(0, 60)
    line21, = ax2.plot(env.x, env.y11, label='at hand')
    line22, = ax2.plot(env.x, env.y12, label='ordered')
    line23, = ax2.plot(env.x, env.y13, label='shortage')
    ax2.legend()
    ax2.grid()

    ax3 = fig.add_subplot(223)

    for t in range(1, 1000):
        env.run(until=t*50)  # stepwise execution
        if t % 50 == 0:
            env.agent.update_epsilon()
            print('epsilon = {}'.format(env.agent.epsilon))
        line1.set_data(env.t, env.z)
        line21.set_data(env.x, env.y11)
        line22.set_data(env.x, env.y12)
        line23.set_data(env.x, env.y13)
        heatmap = ax3.imshow(env.agent.Q, vmin=2, vmax=10, cmap='jet', aspect=0.25)
        bar = plt.colorbar(heatmap, ax=ax3)
        plt.pause(0.1)
        bar.remove()
    plt.show()
# ---------- ---------- ---------- ----------

if __name__ == "__main__":
    main()
